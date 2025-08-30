"""Input conversion from Arrow RecordBatch to Python function arguments."""

import inspect
from typing import Dict, Any, List

try:
    import pyarrow as pa
except ImportError:
    pa = None

from ..utils.type_utils import (
    is_composite_type, get_composite_fields, is_dataframe_type,
    is_list_type, is_dict_type, is_optional_type, get_optional_inner_type,
    get_args_safe
)
from ..schema.validation import get_field_alignment_mapping
from ..error_handling.exceptions import ConversionError
from .dataframe_converter import DataFrameConverter


def convert_input(
    record_batch: 'pa.RecordBatch',
    type_hints: Dict[str, Any],
    signature: inspect.Signature,
    expected_schema: 'pa.Schema',
    input_mode
) -> Dict[str, Any]:
    """
    Convert RecordBatch to function arguments based on input mode.
    
    Args:
        record_batch: Input RecordBatch
        type_hints: Function type hints
        signature: Function signature
        expected_schema: Expected input schema
        input_mode: Processing mode ("record" or "batch")
        
    Returns:
        Dictionary mapping parameter names to converted values
        
    Raises:
        ConversionError: If conversion fails
    """
    if not pa:
        raise ConversionError("PyArrow is required but not installed")
    
    # Get field alignment mapping
    try:
        field_alignment = get_field_alignment_mapping(record_batch.schema, expected_schema)
    except Exception as e:
        raise ConversionError(f"Schema alignment failed: {e}")
    
    # Reorder RecordBatch columns to match expected schema
    aligned_columns = [record_batch.column(i) for i in field_alignment]
    # Convert ChunkedArrays to Arrays if necessary
    aligned_arrays = []
    for col in aligned_columns:
        if isinstance(col, pa.ChunkedArray):
            aligned_arrays.append(col.combine_chunks())
        else:
            aligned_arrays.append(col)
    aligned_batch = pa.record_batch(aligned_arrays, expected_schema)
    
    # Simple mode check - "record" vs "batch"
    if input_mode == "record":
        return _convert_record_input(aligned_batch, type_hints, signature)
    else:  # "batch"
        return _convert_batch_input(aligned_batch, type_hints, signature)


def _convert_record_input(
    record_batch: 'pa.RecordBatch',
    type_hints: Dict[str, Any],
    signature: inspect.Signature
) -> List[Dict[str, Any]]:
    """
    Convert RecordBatch to list of record arguments for record-by-record processing.
    
    Returns:
        List of argument dictionaries, one per record
    """
    num_rows = record_batch.num_rows
    records = []
    
    for row_idx in range(num_rows):
        record_args = {}
        
        for param_name in signature.parameters:
            if param_name not in type_hints:
                continue
            
            param_type = type_hints[param_name]
            
            # Find field in schema
            field_idx = None
            for i, field in enumerate(record_batch.schema):
                if field.name == param_name:
                    field_idx = i
                    break
            
            if field_idx is None:
                raise ConversionError(f"Parameter '{param_name}' not found in schema")
            
            # Extract value from column
            column = record_batch.column(field_idx)
            value = _extract_record_value(column, row_idx, param_type)
            record_args[param_name] = value
        
        records.append(record_args)
    
    return records


def _convert_batch_input(
    record_batch: 'pa.RecordBatch',
    type_hints: Dict[str, Any],
    signature: inspect.Signature
) -> Dict[str, Any]:
    """
    Convert RecordBatch to batch arguments for batch processing.
    
    Returns:
        Single argument dictionary with batch data
    """
    batch_args = {}
    
    for param_name in signature.parameters:
        if param_name not in type_hints:
            continue
        
        param_type = type_hints[param_name]
        
        # Handle DataFrame parameters
        if is_dataframe_type(param_type):
            field_idx = None
            for i, field in enumerate(record_batch.schema):
                if field.name == param_name:
                    field_idx = i
                    break
            
            if field_idx is None:
                raise ConversionError(f"Parameter '{param_name}' not found in schema")
            
            column = record_batch.column(field_idx)
            # Extract struct data and convert to DataFrame
            struct_data = column.to_pylist()[0]  # Get first (and only) row
            
            if struct_data is None:
                # Create empty DataFrame with expected columns
                converter = DataFrameConverter()
                empty_batch = pa.record_batch([], pa.schema([]))
                batch_args[param_name] = converter.to_dataframe(empty_batch, param_type)
            else:
                # Convert struct data to RecordBatch for DataFrame conversion
                column_arrays = []
                column_names = []
                for field_name, field_data in struct_data.items():
                    column_names.append(field_name)
                    column_arrays.append(pa.array(field_data))
                
                df_schema = pa.schema([(name, arr.type) for name, arr in zip(column_names, column_arrays)])
                df_batch = pa.record_batch(column_arrays, df_schema)
                
                converter = DataFrameConverter()
                batch_args[param_name] = converter.to_dataframe(df_batch, param_type)
        
        # Handle list parameters
        elif is_list_type(param_type):
            field_idx = None
            for i, field in enumerate(record_batch.schema):
                if field.name == param_name:
                    field_idx = i
                    break
            
            if field_idx is None:
                raise ConversionError(f"Parameter '{param_name}' not found in schema")
            
            column = record_batch.column(field_idx)
            batch_args[param_name] = _convert_column_to_list(column, param_type)
        
        # Handle dict parameters
        elif is_dict_type(param_type):
            field_idx = None
            for i, field in enumerate(record_batch.schema):
                if field.name == param_name:
                    field_idx = i
                    break
            
            if field_idx is None:
                raise ConversionError(f"Parameter '{param_name}' not found in schema")
            
            column = record_batch.column(field_idx)
            batch_args[param_name] = _convert_column_to_dict(column, param_type)
        
        # Handle composite types with all list fields
        elif is_composite_type(param_type):
            field_idx = None
            for i, field in enumerate(record_batch.schema):
                if field.name == param_name:
                    field_idx = i
                    break
            
            if field_idx is None:
                raise ConversionError(f"Parameter '{param_name}' not found in schema")
            
            column = record_batch.column(field_idx)
            composite_data = _convert_composite_from_column(column, param_type)
            batch_args[param_name] = composite_data
    
    return batch_args


def _extract_record_value(column: 'pa.ChunkedArray', row_idx: int, param_type: Any) -> Any:
    """Extract a single value from a column for record processing."""
    # Get scalar value
    scalar_value = column[row_idx]
    
    # Handle null values
    if scalar_value.is_valid is False:
        if is_optional_type(param_type):
            return None
        else:
            raise ConversionError(f"Null value for non-optional parameter of type {param_type}")
    
    # Convert Arrow scalar to Python value
    python_value = scalar_value.as_py()
    
    # Handle composite types
    if is_composite_type(param_type):
        return _convert_struct_value(python_value, param_type)
    
    # Handle list types with composite elements
    if is_list_type(param_type):
        if isinstance(python_value, list):
            args = get_args_safe(param_type)
            if args and is_composite_type(args[0]):
                element_type = args[0]
                return [_convert_struct_value(item, element_type) if item is not None else None 
                        for item in python_value]
            else:
                return python_value
        else:
            return python_value
    
    # Handle dict types (Map in Arrow)
    if is_dict_type(param_type):
        if isinstance(python_value, list):
            return dict(python_value)
        elif isinstance(python_value, dict):
            return python_value
        else:
            return {}
    
    return python_value


def _convert_column_to_list(column: 'pa.ChunkedArray', param_type: Any) -> List[Any]:
    """Convert an Arrow column to a Python list for batch processing."""
    python_list = column.to_pylist()
    
    # For batch processing with list parameters, we expect a single row
    # containing the list data, so extract the first (and only) row
    if len(python_list) == 1 and isinstance(python_list[0], list):
        list_data = python_list[0]
    else:
        # Multiple rows - flatten or use as-is depending on the context
        list_data = python_list
    
    # Handle composite element types
    args = get_args_safe(param_type)
    if args and is_composite_type(args[0]):
        element_type = args[0]
        return [_convert_struct_value(item, element_type) if item is not None else None 
                for item in list_data]
    
    return list_data


def _convert_composite_from_column(column: 'pa.ChunkedArray', composite_type: Any) -> Any:
    """Convert a struct column to composite type with all list fields."""
    # Get the struct data from the first (and only) row
    struct_data = column.to_pylist()[0]
    
    if struct_data is None:
        return None
    
    fields = get_composite_fields(composite_type)
    field_data = {}
    
    for field_name, field_type in fields.items():
        if field_name not in struct_data:
            raise ConversionError(f"Field '{field_name}' not found in struct data")
        
        field_value = struct_data[field_name]
        field_data[field_name] = field_value
    
    # Create instance of composite type
    return _create_composite_instance(composite_type, field_data)


def _convert_composite_batch(record_batch: 'pa.RecordBatch', composite_type: Any) -> Any:
    """Convert RecordBatch to composite type with all list fields."""
    fields = get_composite_fields(composite_type)
    field_data = {}
    
    for field_name, field_type in fields.items():
        # Find column
        field_idx = None
        for i, field in enumerate(record_batch.schema):
            if field.name == field_name:
                field_idx = i
                break
        
        if field_idx is None:
            raise ConversionError(f"Field '{field_name}' not found in schema")
        
        column = record_batch.column(field_idx)
        field_data[field_name] = _convert_column_to_list(column, field_type)
    
    # Create instance of composite type
    return _create_composite_instance(composite_type, field_data)


def _convert_struct_value(struct_dict: dict, composite_type: Any) -> Any:
    """Convert a struct dictionary to composite type instance."""
    if struct_dict is None:
        return None
    
    return _create_composite_instance(composite_type, struct_dict)


def _create_composite_instance(composite_type: Any, field_data: dict) -> Any:
    """Create an instance of a composite type from field data."""
    from dataclasses import is_dataclass
    
    inner_type = get_optional_inner_type(composite_type)
    
    # Dataclass
    if is_dataclass(inner_type):
        return inner_type(**field_data)
    
    # NamedTuple
    elif hasattr(inner_type, '_fields'):
        return inner_type(**field_data)
    
    # TypedDict - return as regular dict
    elif hasattr(inner_type, '__annotations__'):
        return field_data
    
    else:
        raise ConversionError(f"Unknown composite type: {composite_type}")


def _convert_column_to_dict(column: 'pa.ChunkedArray', param_type: Any) -> dict:
    """Convert an Arrow Map column to a Python dictionary."""
    python_list = column.to_pylist()
    
    # For record processing, extract the value from the specific row
    # For batch processing, we expect a single row containing the map data
    if len(python_list) == 1:
        map_data = python_list[0]
    else:
        # Multiple rows - this shouldn't happen for batch processing
        # but handle it gracefully
        map_data = python_list[0] if python_list else []
    
    # Convert list of tuples to dictionary
    if isinstance(map_data, list):
        return dict(map_data)
    elif isinstance(map_data, dict):
        return map_data
    else:
        return {}