"""Output conversion from Python function results to Arrow RecordBatch."""

from typing import Any, List, Dict, Optional, Tuple

try:
    import pyarrow as pa
except ImportError:
    pa = None

from ..utils.type_utils import (
    is_composite_type, get_composite_fields, is_dataframe_type,
    is_list_type, get_args_safe, is_optional_type, get_optional_inner_type
)
from ..error_handling.exceptions import ConversionError
from .dataframe_converter import DataFrameConverter


def convert_output(
    results: List[Any], 
    output_schema: Optional['pa.Schema'],
    processing_mode
) -> Optional['pa.RecordBatch']:
    """
    Convert function results to output RecordBatch.
    
    Args:
        results: List of function results
        output_schema: Expected output schema (None if no output)
        processing_mode: ProcessingMode (RECORD_TO_RECORD, RECORD_TO_BATCH, or BATCH_TO_BATCH)
        
    Returns:
        RecordBatch with results, or None if no output schema
        
    Raises:
        ConversionError: If conversion fails
    """
    if not pa:
        raise ConversionError("PyArrow is required but not installed")
    
    if not output_schema:
        return None
    
    if not results:
        # Empty results - return empty RecordBatch
        return pa.record_batch([], output_schema)
    
    from ..processing.mode_detection import ProcessingMode
    
    if processing_mode == ProcessingMode.RECORD_TO_BATCH:
        # Record-to-batch: multiple list results from individual records
        return _convert_record_to_batch_output(results, output_schema)
    elif processing_mode == ProcessingMode.BATCH_TO_BATCH:
        # True batch processing: single result from batch input
        return _convert_batch_output(results, output_schema)
    else:
        # RECORD_TO_RECORD - individual results become records
        return _convert_record_output(results, output_schema)


def _convert_record_to_batch_output(results: List[Any], output_schema: 'pa.Schema') -> 'pa.RecordBatch':
    """Convert record-to-batch processing results to RecordBatch."""
    if not results:
        return pa.record_batch([], output_schema)
    
    # Check what type of results we have
    first_result = results[0]
    
    # Case 1: Simple list results (single column output)
    if isinstance(first_result, list) and len(output_schema) == 1:
        field = output_schema[0]
        flattened_data = []
        
        # Flatten all list results into a single list
        for result in results:
            if isinstance(result, list):
                flattened_data.extend(result)
            else:
                # Single item, treat as list of one
                flattened_data.append(result)
        
        # Create column array from flattened data
        try:
            column_data = [pa.array(flattened_data, type=field.type)]
            return pa.record_batch(column_data, output_schema)
        except Exception as e:
            raise ConversionError(f"Failed to create batch output from list results: {e}")
    
    # Case 2: List of composite objects (e.g., List[DataClass])
    elif isinstance(first_result, list) and (len(first_result) == 0 or is_composite_type(type(first_result[0]))):
        # Function returned List[CompositeType] - flatten all results
        flattened_objects = []
        for result in results:
            if isinstance(result, list):
                flattened_objects.extend(result)
            else:
                flattened_objects.append(result)
        
        # Convert list of composite objects to column data
        if not flattened_objects:
            # Create empty arrays for each field in the schema
            empty_arrays = []
            for field in output_schema:
                empty_arrays.append(pa.array([], type=field.type))
            return pa.record_batch(empty_arrays, output_schema)
        
        # Convert to columns using standard record conversion
        column_data = _results_to_columns(flattened_objects, output_schema)
        return pa.record_batch(column_data, output_schema)
    
    # Case 3: DataFrame results 
    elif is_dataframe_type(type(first_result)):
        # Function returned DataFrame - flatten all DataFrame results
        from .dataframe_converter import DataFrameConverter
        converter = DataFrameConverter()
        
        # Collect all DataFrames and concatenate them
        all_dataframes = []
        for result in results:
            if is_dataframe_type(type(result)):
                all_dataframes.append(result)
            else:
                raise ConversionError(f"Mixed result types in record-to-batch mode: expected DataFrame, got {type(result)}")
        
        if not all_dataframes:
            # Create empty arrays for each field in the schema
            empty_arrays = []
            for field in output_schema:
                empty_arrays.append(pa.array([], type=field.type))
            return pa.record_batch(empty_arrays, output_schema)
        
        # Concatenate all DataFrames
        if len(all_dataframes) == 1:
            combined_df = all_dataframes[0]
        else:
            # For multiple DataFrames, we need to concatenate them
            # This handles the case where multiple input records each return a DataFrame
            first_df = all_dataframes[0]
            
            # Check if it's Polars or Pandas
            if hasattr(first_df, 'height'):  # Polars DataFrames have 'height' attribute
                import polars as pl
                combined_df = pl.concat(all_dataframes)
            else:  # Pandas
                import pandas as pd
                combined_df = pd.concat(all_dataframes, ignore_index=True)
        
        # Convert the combined DataFrame to RecordBatch
        return converter.from_dataframe(combined_df, output_schema)
    
    # Case 4: Composite results with list fields (multi-column output)
    elif is_composite_type(type(first_result)):
        # Each result should be a composite object with list fields
        # We need to collect all the lists from each field across all results
        column_data = {}
        
        # Initialize column data for each field
        for field in output_schema:
            column_data[field.name] = []
        
        # Collect data from each result
        for result in results:
            if result is None:
                # Handle None results - add empty lists to all columns
                for field in output_schema:
                    column_data[field.name].extend([])
            elif is_composite_type(type(result)):
                # Extract field values from composite result
                result_fields = get_composite_fields(type(result))
                for field_name, field_type in result_fields.items():
                    if field_name in column_data:
                        field_value = getattr(result, field_name)
                        if isinstance(field_value, list):
                            column_data[field_name].extend(field_value)
                        else:
                            column_data[field_name].append(field_value)
            else:
                raise ConversionError(f"Expected composite result in record-to-batch mode, got {type(result)}")
        
        # Create Arrow arrays for each column
        try:
            arrays = []
            for field in output_schema:
                field_data = column_data[field.name]
                arrays.append(pa.array(field_data, type=field.type))
            
            return pa.record_batch(arrays, output_schema)
        except Exception as e:
            raise ConversionError(f"Failed to create batch output from composite results: {e}")
    
    else:
        raise ConversionError(f"Unsupported result type for record-to-batch mode: {type(first_result)}")


def _convert_record_output(results: List[Any], output_schema: 'pa.Schema') -> 'pa.RecordBatch':
    """Convert record processing results to RecordBatch."""
    if not results:
        return pa.record_batch([], output_schema)
    
    # Handle list return types (one-to-many)
    flattened_results = []
    for result in results:
        if isinstance(result, list):
            flattened_results.extend(result)
        else:
            flattened_results.append(result)
    
    if not flattened_results:
        return pa.record_batch([], output_schema)
    
    # Convert results to column data
    column_data = _results_to_columns(flattened_results, output_schema)
    
    # Create RecordBatch
    return pa.record_batch(column_data, output_schema)


def _convert_batch_output(results: List[Any], output_schema: 'pa.Schema') -> 'pa.RecordBatch':
    """Convert batch processing results to RecordBatch."""
    if len(results) != 1:
        raise ConversionError(f"Batch processing should produce exactly 1 result, got {len(results)}")
    
    result = results[0]
    
    # Handle DataFrame results
    if is_dataframe_type(type(result)):
        converter = DataFrameConverter()
        return converter.from_dataframe(result, output_schema)
    
    # Handle scalar results (with explicit schema)
    if not is_composite_type(type(result)) and not isinstance(result, list):
        # Single scalar result - create single-row RecordBatch
        if len(output_schema) != 1:
            raise ConversionError(f"Scalar result requires single-field schema, got {len(output_schema)} fields")
        
        field = output_schema[0]
        column_data = [pa.array([result], type=field.type)]
        return pa.record_batch(column_data, output_schema)
    
    # Handle list results (with explicit schema)
    if isinstance(result, list) and len(output_schema) == 1:
        field = output_schema[0]
        # For list field types, wrap the result to create single-row batch
        if pa.types.is_list(field.type):
            column_data = [pa.array([result], type=field.type)]
        else:
            # For non-list field types, result is multiple rows
            column_data = [pa.array(result, type=field.type)]
        return pa.record_batch(column_data, output_schema)
    
    # Handle composite results
    if is_composite_type(type(result)):
        return _convert_composite_batch_result(result, output_schema)
    
    raise ConversionError(f"Unsupported batch result type: {type(result)}")


def _results_to_columns(results: List[Any], schema: 'pa.Schema') -> List['pa.Array']:
    """Convert list of results to column arrays."""
    column_data = {}
    
    # Initialize columns
    for field in schema:
        column_data[field.name] = []
    
    # Process each result
    for result in results:
        if result is None:
            # Handle None results - add nulls to all columns
            for field in schema:
                column_data[field.name].append(None)
        
        elif is_composite_type(type(result)):
            # Handle composite results
            if len(schema) == 1:
                field = schema[0]
                if pa.types.is_struct(field.type):
                    # Single struct field - convert composite to struct value
                    result_dict = _composite_to_dict(result)
                    column_data[field.name].append(result_dict)
                else:
                    # Single non-struct field - this shouldn't happen for composite results
                    raise ConversionError(f"Cannot map composite result to non-struct field '{field.name}'")
            else:
                # Multiple fields - extract fields from composite result
                result_dict = _composite_to_dict(result)
                for field in schema:
                    value = result_dict.get(field.name)
                    column_data[field.name].append(value)
        
        elif len(schema) == 1:
            # Single field schema - result is the value
            field = schema[0]
            column_data[field.name].append(result)
        
        else:
            raise ConversionError(f"Cannot map result {result} to schema with {len(schema)} fields")
    
    # Convert to Arrow arrays
    arrays = []
    for field in schema:
        values = column_data[field.name]
        try:
            array = pa.array(values, type=field.type)
            arrays.append(array)
        except Exception as e:
            raise ConversionError(f"Failed to create array for field '{field.name}': {e}")
    
    return arrays


def _convert_composite_batch_result(result: Any, schema: 'pa.Schema') -> 'pa.RecordBatch':
    """Convert composite batch result to RecordBatch."""
    result_dict = _composite_to_dict(result)
    
    # Check if schema has single field with struct type
    if len(schema) == 1:
        field = schema[0]
        if pa.types.is_struct(field.type):
            # Single struct field - wrap the composite result
            column_data = [pa.array([result_dict], type=field.type)]
            return pa.record_batch(column_data, schema)
    
    # Handle case where composite has all list fields (RecordBatch schema)
    fields = get_composite_fields(type(result))
    if all(is_list_type(field_type) for field_type in fields.values()):
        # Lists represent columns
        column_data = []
        for field in schema:
            if field.name not in result_dict:
                raise ConversionError(f"Missing field '{field.name}' in result")
            
            values = result_dict[field.name]
            if not isinstance(values, list):
                raise ConversionError(f"Expected list for field '{field.name}', got {type(values)}")
            
            try:
                array = pa.array(values, type=field.type)
                column_data.append(array)
            except Exception as e:
                raise ConversionError(f"Failed to create array for field '{field.name}': {e}")
        
        return pa.record_batch(column_data, schema)
    
    else:
        # Single record result
        return _convert_record_output([result], schema)


def _composite_to_dict(obj: Any) -> Dict[str, Any]:
    """Convert composite object to dictionary."""
    from dataclasses import is_dataclass, asdict
    
    if obj is None:
        return {}
    
    # Dataclass
    if is_dataclass(obj):
        return asdict(obj)
    
    # NamedTuple
    elif hasattr(obj, '_asdict'):
        return obj._asdict()
    
    # TypedDict (already a dict)
    elif isinstance(obj, dict):
        return obj
    
    else:
        raise ConversionError(f"Cannot convert {type(obj)} to dictionary")


def convert_error_output(
    error_records: List[Dict[str, Any]], 
    error_schema: 'pa.Schema'
) -> Optional['pa.RecordBatch']:
    """
    Convert error records to error RecordBatch.
    
    Args:
        error_records: List of error record dictionaries
        error_schema: Error schema
        
    Returns:
        RecordBatch with error records, or None if no errors
    """
    if not pa:
        raise ConversionError("PyArrow is required but not installed")
    
    if not error_records:
        return None
    
    # Convert to column data
    column_data = {}
    for field in error_schema:
        column_data[field.name] = []
    
    for record in error_records:
        for field in error_schema:
            value = record.get(field.name)
            column_data[field.name].append(value)
    
    # Create arrays
    arrays = []
    for field in error_schema:
        values = column_data[field.name]
        try:
            array = pa.array(values, type=field.type)
            arrays.append(array)
        except Exception as e:
            raise ConversionError(f"Failed to create error array for field '{field.name}': {e}")
    
    return pa.record_batch(arrays, error_schema)