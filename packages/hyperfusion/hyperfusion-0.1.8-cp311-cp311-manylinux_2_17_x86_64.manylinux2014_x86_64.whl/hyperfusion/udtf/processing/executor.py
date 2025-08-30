"""Main execution logic for UDTF functions."""

import asyncio
from typing import Tuple, Optional

try:
    import pyarrow as pa
except ImportError:
    pa = None

from .mode_detection import ProcessingMode, is_record_input_processing
from .record_processor import RecordProcessor
from .batch_processor import BatchProcessor
from ..schema.validation import validate_record_batch_schema
from ..error_handling.exceptions import ProcessingError


async def execute_udtf(udtf_function, record_batch: 'pa.RecordBatch') -> Tuple[Optional['pa.RecordBatch'], Optional['pa.RecordBatch']]:
    """
    Execute a UDTF function on a RecordBatch asynchronously.
    
    Args:
        udtf_function: UDTFFunction instance with all configuration
        record_batch: Input RecordBatch to process
        
    Returns:
        Tuple of (success_batch, error_batch)
        
    Raises:
        ProcessingError: If execution fails
    """
    if not pa:
        raise ProcessingError("PyArrow is required but not installed")
    
    # Validate input schema
    try:
        validate_record_batch_schema(record_batch, udtf_function.input_schema)
    except Exception as e:
        raise ProcessingError(f"Input schema validation failed: {e}")
    
    # Create appropriate processor based on processing mode
    if is_record_input_processing(udtf_function.processing_mode):
        processor = RecordProcessor(
            udtf_function.func,
            udtf_function.type_hints,
            udtf_function.signature,
            udtf_function.input_schema,
            udtf_function.output_schema,
            udtf_function.error_schema,
            udtf_function.processing_mode
        )
    else:
        processor = BatchProcessor(
            udtf_function.func,
            udtf_function.type_hints,
            udtf_function.signature,
            udtf_function.input_schema,
            udtf_function.output_schema,
            udtf_function.error_schema,
            udtf_function.processing_mode
        )
    
    # Execute processing
    try:
        return await processor.process(record_batch)
    except Exception as e:
        raise ProcessingError(f"Function execution failed: {e}")


def execute_udtf_sync(udtf_function, record_batch: 'pa.RecordBatch') -> Tuple[Optional['pa.RecordBatch'], Optional['pa.RecordBatch']]:
    """
    Execute a UDTF function on a RecordBatch synchronously (backward compatibility).
    
    Args:
        udtf_function: UDTFFunction instance with all configuration
        record_batch: Input RecordBatch to process
        
    Returns:
        Tuple of (success_batch, error_batch)
        
    Raises:
        ProcessingError: If execution fails
    """
    try:
        # Try to get the current event loop
        loop = asyncio.get_running_loop()
        # If we're in an event loop, we can't use asyncio.run()
        raise ProcessingError("Cannot call sync method from within an async context. Use execute_udtf() instead.")
    except RuntimeError as e:
        if "no running event loop" in str(e).lower():
            # No event loop running, safe to use asyncio.run()
            return asyncio.run(execute_udtf(udtf_function, record_batch))
        else:
            # Re-raise as ProcessingError
            raise ProcessingError(f"Event loop error: {e}")


class UDTFExecutor:
    """High-level executor for UDTF operations."""
    
    def __init__(self, udtf_function):
        """
        Initialize executor with UDTF function.
        
        Args:
            udtf_function: UDTFFunction instance
        """
        self.udtf_function = udtf_function
    
    def execute(self, record_batch: 'pa.RecordBatch') -> Tuple[Optional['pa.RecordBatch'], Optional['pa.RecordBatch']]:
        """
        Execute the UDTF function synchronously (backward compatibility).
        
        Args:
            record_batch: Input RecordBatch
            
        Returns:
            Tuple of (success_batch, error_batch)
        """
        try:
            # Try to get the current event loop
            loop = asyncio.get_running_loop()
            # If we're in an event loop, we can't use asyncio.run()
            raise ProcessingError("Cannot call sync method from within an async context. Use execute_async() instead.")
        except RuntimeError as e:
            if "no running event loop" in str(e).lower():
                # No event loop running, safe to use asyncio.run()
                return asyncio.run(self.execute_async(record_batch))
            else:
                # Re-raise as ProcessingError
                raise ProcessingError(f"Event loop error: {e}")
    
    async def execute_async(self, record_batch: 'pa.RecordBatch') -> Tuple[Optional['pa.RecordBatch'], Optional['pa.RecordBatch']]:
        """
        Execute the UDTF function asynchronously.
        
        Args:
            record_batch: Input RecordBatch
            
        Returns:
            Tuple of (success_batch, error_batch)
        """
        return await execute_udtf(self.udtf_function, record_batch)
    
    def get_input_schema(self) -> 'pa.Schema':
        """Get the input schema."""
        return self.udtf_function.input_schema
    
    def get_output_schema(self) -> Optional['pa.Schema']:
        """Get the output schema."""
        return self.udtf_function.output_schema
    
    def get_error_schema(self) -> Optional['pa.Schema']:
        """Get the error schema."""
        return self.udtf_function.error_schema
    
    def get_processing_mode(self) -> ProcessingMode:
        """Get the processing mode."""
        return self.udtf_function.processing_mode
    
    
    def describe(self) -> dict:
        """Get a description of the UDTF configuration.""" 
        from .mode_detection import get_processing_reason
        
        mode = self.udtf_function.processing_mode
        reason = get_processing_reason(
            mode, 
            self.udtf_function.type_hints, 
            self.udtf_function.signature,
            self.udtf_function.type_hints.get('return')
        )
        
        return {
            'function_name': self.udtf_function.func.__name__,
            'processing_mode': mode.value,
            'processing_reason': reason,
            'input_schema': str(self.udtf_function.input_schema),
            'output_schema': str(self.udtf_function.output_schema) if self.udtf_function.output_schema else None,
            'error_schema': str(self.udtf_function.error_schema) if self.udtf_function.error_schema else None,
            'has_explicit_input_schema': self.udtf_function.explicit_input_schema is not None,
            'has_explicit_output_schema': self.udtf_function.explicit_output_schema is not None,  
            'has_explicit_error_schema': self.udtf_function.explicit_error_schema is not None,
        }