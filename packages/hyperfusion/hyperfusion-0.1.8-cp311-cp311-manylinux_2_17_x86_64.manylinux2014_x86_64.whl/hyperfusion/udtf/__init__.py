"""Arrow UDTF: A system for mapping Apache Arrow RecordBatches to Python functions."""

from .decorator import udtf, UDTFFunction
from .registry import registry
from .processing.executor import execute_udtf, execute_udtf_sync, UDTFExecutor

__all__ = ["udtf", "UDTFFunction", "registry", "execute_udtf", "execute_udtf_sync", "UDTFExecutor"]