"""Processing functionality for record and batch modes."""

from .mode_detection import (
    determine_processing_mode,
    ProcessingMode,
    is_record_input_processing,
    is_batch_input_processing,
    is_record_output,
    is_batch_output,
    get_processing_reason
)
from .record_processor import RecordProcessor
from .batch_processor import BatchProcessor
from .executor import execute_udtf

__all__ = [
    "determine_processing_mode",
    "ProcessingMode",
    "is_record_input_processing",
    "is_batch_input_processing", 
    "is_record_output",
    "is_batch_output",
    "get_processing_reason",
    "RecordProcessor",
    "BatchProcessor", 
    "execute_udtf"
]