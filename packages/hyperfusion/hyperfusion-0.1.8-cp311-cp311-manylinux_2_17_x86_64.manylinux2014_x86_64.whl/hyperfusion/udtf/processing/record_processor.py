"""Record-by-record processing implementation."""

import asyncio
import inspect
from typing import List, Dict, Any, Tuple, Optional, Callable

try:
    import pyarrow as pa
except ImportError:
    pa = None

from ..conversion.input_converter import convert_input
from ..conversion.output_converter import convert_output, convert_error_output
from ..error_handling.error_schemas import add_exception_to_record
from ..error_handling.exceptions import ProcessingError
from ..utils.type_utils import is_tuple_type, get_args_safe


class RecordProcessor:
    """Processes functions in record-by-record mode."""
    
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
        Process RecordBatch in record-by-record mode asynchronously.
        
        Args:
            record_batch: Input RecordBatch
            
        Returns:
            Tuple of (success_batch, error_batch)
        """
        if not pa:
            raise ProcessingError("PyArrow is required but not installed")
        
        # Convert input to list of record arguments
        try:
            from .mode_detection import ProcessingMode
            # For record processor, we always use record-by-record conversion
            record_args_list = convert_input(
                record_batch, 
                self.type_hints, 
                self.signature, 
                self.input_schema, 
                "record"  # Simplified conversion mode
            )
        except Exception as e:
            raise ProcessingError(f"Input conversion failed: {e}")
        
        # Process each record
        success_results = []
        error_records = []
        
        for row_idx, record_args in enumerate(record_args_list):
            try:
                result = await self.func(**record_args)
                
                if self.returns_tuple:
                    success_result, error_result = result
                    
                    if success_result is not None:
                        success_results.append(success_result)
                    
                    if error_result is not None:
                        # Convert error result to record with exception field
                        error_record = self._create_error_record(error_result, None, record_args)
                        error_records.append(error_record)
                
                else:
                    success_results.append(result)
            
            except Exception as e:
                # Create error record with exception
                error_record = self._create_error_record(None, e, record_args)
                error_records.append(error_record)
        
        # Convert results to RecordBatches
        success_batch = None
        if self.output_schema and success_results:
            try:
                success_batch = convert_output(success_results, self.output_schema, self.processing_mode)
            except Exception as e:
                raise ProcessingError(f"Success output conversion failed: {e}")
        
        error_batch = None
        if self.error_schema and error_records:
            try:
                error_batch = convert_error_output(error_records, self.error_schema)
            except Exception as e:
                raise ProcessingError(f"Error output conversion failed: {e}")
        
        return success_batch, error_batch
    
    def _create_error_record(
        self, 
        error_result: Any, 
        exception: Optional[Exception], 
        input_record: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create an error record from error result or exception."""
        if error_result is not None:
            # Custom error result
            if hasattr(error_result, '__dict__'):
                error_record = vars(error_result)
            elif hasattr(error_result, '_asdict'):
                error_record = error_result._asdict()
            elif isinstance(error_result, dict):
                error_record = error_result.copy()
            else:
                raise ProcessingError(f"Cannot convert error result {type(error_result)} to record")
            
            # Add exception field (empty for custom errors)
            error_record['exception'] = None
        
        else:
            # Exception occurred - use default error schema (input + exception)
            error_record = input_record.copy()
            error_record['exception'] = str(exception) if exception else "Unknown error"
        
        return error_record