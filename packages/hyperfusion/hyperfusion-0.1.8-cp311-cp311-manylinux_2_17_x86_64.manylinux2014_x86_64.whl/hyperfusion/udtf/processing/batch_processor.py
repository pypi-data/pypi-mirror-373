"""Batch processing implementation."""

import asyncio
import inspect
from typing import Dict, Any, Tuple, Optional, Callable

try:
    import pyarrow as pa
except ImportError:
    pa = None

from ..conversion.input_converter import convert_input
from ..conversion.output_converter import convert_output, convert_error_output
from ..error_handling.error_schemas import add_exception_to_record
from ..error_handling.exceptions import ProcessingError
from ..utils.type_utils import is_tuple_type


class BatchProcessor:
    """Processes functions in batch mode."""
    
    def __init__(
        self,
        func: Callable,
        type_hints: Dict[str, Any],
        signature: inspect.Signature,
        input_schema: 'pa.Schema',
        output_schema: Optional['pa.Schema'],
        error_schema: Optional['pa.Schema'],
        processing_mode=None
    ):
        self.func = func
        self.type_hints = type_hints
        self.signature = signature
        self.input_schema = input_schema
        self.output_schema = output_schema
        self.error_schema = error_schema
        self.processing_mode = processing_mode
        
        # Determine if function returns tuple (success, error)
        return_type = type_hints.get('return')
        self.returns_tuple = is_tuple_type(return_type)
    
    async def process(self, record_batch: 'pa.RecordBatch') -> Tuple[Optional['pa.RecordBatch'], Optional['pa.RecordBatch']]:
        """
        Process RecordBatch in batch mode asynchronously.
        
        Args:
            record_batch: Input RecordBatch
            
        Returns:
            Tuple of (success_batch, error_batch)
        """
        if not pa:
            raise ProcessingError("PyArrow is required but not installed")
        
        # Convert input to batch arguments
        try:
            from .mode_detection import ProcessingMode
            # For batch processor, we always use batch conversion
            batch_args = convert_input(
                record_batch, 
                self.type_hints, 
                self.signature, 
                self.input_schema, 
                "batch"  # Simplified conversion mode
            )
        except Exception as e:
            raise ProcessingError(f"Input conversion failed: {e}")
        
        try:
            # Execute function with batch arguments
            result = await self.func(**batch_args)
            
            if self.returns_tuple:
                success_result, error_result = result
                
                # Convert success result
                success_batch = None
                if success_result is not None and self.output_schema:
                    try:
                        success_batch = convert_output([success_result], self.output_schema, self.processing_mode)
                    except Exception as e:
                        raise ProcessingError(f"Success output conversion failed: {e}")
                
                # Convert error result
                error_batch = None
                if error_result is not None and self.error_schema:
                    try:
                        # For batch processing, error result should be structured data
                        error_records = self._convert_error_result_to_records(error_result)
                        error_batch = convert_error_output(error_records, self.error_schema)
                    except Exception as e:
                        raise ProcessingError(f"Error output conversion failed: {e}")
                
                return success_batch, error_batch
            
            else:
                # Single result
                success_batch = None
                if result is not None and self.output_schema:
                    try:
                        success_batch = convert_output([result], self.output_schema, self.processing_mode)
                    except Exception as e:
                        raise ProcessingError(f"Output conversion failed: {e}")
                
                return success_batch, None
        
        except Exception as e:
            # Batch processing failure - entire batch goes to error output
            return self._handle_batch_exception(e, record_batch)
    
    def _handle_batch_exception(
        self, 
        exception: Exception, 
        input_batch: 'pa.RecordBatch'
    ) -> Tuple[None, Optional['pa.RecordBatch']]:
        """Handle exception in batch processing by sending entire batch to error output."""
        if not self.error_schema:
            # No error schema - cannot capture errors
            raise ProcessingError(f"Batch processing failed and no error schema available: {exception}")
        
        try:
            # Convert entire input batch to error records
            error_records = []
            
            # Convert input batch to list of dictionaries
            input_dict = input_batch.to_pydict()
            
            # For batch processing, check if we should unroll to individual records
            if input_batch.num_rows == 1:
                should_unroll = self._should_unroll_batch_for_errors(input_batch)
                
                if should_unroll:
                    # Unroll batch to individual error records
                    first_row_data = {}
                    max_length = 0
                    
                    for field_name, column_values in input_dict.items():
                        values = column_values[0]  # Get first (and only) row
                        if isinstance(values, list):
                            first_row_data[field_name] = values
                            max_length = max(max_length, len(values))
                        else:
                            first_row_data[field_name] = values
                    
                    # Create individual error records
                    for i in range(max_length if max_length > 0 else 1):
                        error_record = {}
                        for field_name, values in first_row_data.items():
                            if isinstance(values, list) and i < len(values):
                                error_record[field_name] = values[i]
                            elif isinstance(values, list):
                                error_record[field_name] = None
                            else:
                                error_record[field_name] = values
                        
                        # Add exception information
                        error_record['exception'] = str(exception)
                        error_records.append(error_record)
                else:
                    # Keep batch structure
                    error_record = {}
                    for field_name, column_values in input_dict.items():
                        error_record[field_name] = column_values[0]
                    error_record['exception'] = str(exception)
                    error_records.append(error_record)
            else:
                # Multiple rows - treat each row as an error record
                for row_idx in range(input_batch.num_rows):
                    error_record = {}
                    for field_name, column_values in input_dict.items():
                        error_record[field_name] = column_values[row_idx]
                    
                    # Add exception information
                    error_record['exception'] = str(exception)
                    error_records.append(error_record)
            
            # Convert to error batch
            error_batch = convert_error_output(error_records, self.error_schema)
            return None, error_batch
        
        except Exception as conversion_error:
            raise ProcessingError(
                f"Batch processing failed: {exception}. "
                f"Additionally, error conversion failed: {conversion_error}"
            )
    
    def _should_unroll_batch_for_errors(self, input_batch: 'pa.RecordBatch') -> bool:
        """
        Determine if batch should be unrolled to individual records for error reporting.
        
        Returns True if the error schema expects individual records rather than batch structure.
        """
        if not self.error_schema:
            return False
        
        # Check if error schema has scalar types for fields that are lists in input
        for input_field in input_batch.schema:
            if pa.types.is_list(input_field.type):
                # Input field is a list, check if error schema has scalar type for same field
                for error_field in self.error_schema:
                    if error_field.name == input_field.name:
                        if not pa.types.is_list(error_field.type):
                            # Error schema expects scalar but input has list - should unroll
                            return True
                        break
        
        return False
    
    def _convert_error_result_to_records(self, error_result: Any) -> list[dict]:
        """Convert error result to list of error record dictionaries."""
        from dataclasses import is_dataclass, asdict
        from ..utils.type_utils import is_composite_type, has_all_list_fields, get_composite_fields
        
        if error_result is None:
            return []
        
        # Handle composite types
        if is_composite_type(type(error_result)):
            if has_all_list_fields(type(error_result)):
                # Error result with list fields - each index is an error record
                if is_dataclass(error_result):
                    error_dict = asdict(error_result)
                elif hasattr(error_result, '_asdict'):
                    error_dict = error_result._asdict()
                elif isinstance(error_result, dict):
                    error_dict = error_result
                else:
                    raise ProcessingError(f"Cannot convert error result {type(error_result)} to dict")
                
                # Convert list fields to records
                fields = get_composite_fields(type(error_result))
                field_names = list(fields.keys())
                
                if not field_names:
                    return []
                
                # Get length from first field
                first_field_values = error_dict[field_names[0]]
                if not isinstance(first_field_values, list):
                    raise ProcessingError(f"Expected list for error field '{field_names[0]}'")
                
                num_errors = len(first_field_values)
                error_records = []
                
                for i in range(num_errors):
                    record = {}
                    for field_name in field_names:
                        field_values = error_dict[field_name]
                        if not isinstance(field_values, list) or len(field_values) != num_errors:
                            raise ProcessingError(f"Inconsistent error field lengths")
                        record[field_name] = field_values[i]
                    
                    # Exception field will be added by convert_error_output
                    record['exception'] = None
                    error_records.append(record)
                
                return error_records
            
            else:
                # Single error record
                if is_dataclass(error_result):
                    error_record = asdict(error_result)
                elif hasattr(error_result, '_asdict'):
                    error_record = error_result._asdict()
                elif isinstance(error_result, dict):
                    error_record = error_result.copy()
                else:
                    raise ProcessingError(f"Cannot convert error result {type(error_result)} to dict")
                
                error_record['exception'] = None
                return [error_record]
        
        else:
            raise ProcessingError(f"Unsupported error result type: {type(error_result)}")