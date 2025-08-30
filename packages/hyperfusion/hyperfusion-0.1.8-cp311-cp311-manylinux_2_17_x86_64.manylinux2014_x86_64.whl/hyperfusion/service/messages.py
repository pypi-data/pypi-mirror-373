"""Message classes for bus communication."""

from dataclasses import dataclass
from typing import Any, Optional
import pyarrow as pa


@dataclass
class ExecuteFunctionRequest:
    """Message sent to request function execution."""
    exec_msg: Any


@dataclass
class LogMessage:
    """Message for log forwarding."""
    level: str
    message: str


@dataclass
class UDTFExecutionRequest:
    """Request to execute a UDTF."""
    function_name: str
    batch_id: str  # Renamed from execution_id/uuid
    input_data: pa.Table


@dataclass 
class UDTFExecutionResult:
    """Result of UDTF execution."""
    function_name: str
    batch_id: str  # Renamed from execution_id/uuid
    output_data: Optional[pa.Table] = None
    error_data: Optional[pa.Table] = None
    error_message: Optional[str] = None