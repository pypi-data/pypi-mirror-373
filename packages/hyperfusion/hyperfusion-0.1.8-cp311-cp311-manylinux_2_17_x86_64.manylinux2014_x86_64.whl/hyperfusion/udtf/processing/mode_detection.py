"""Processing mode detection for UDTF functions."""

import inspect
from enum import Enum
from typing import Dict, Any, get_origin, get_args, Optional, List, Tuple
import pandas as pd

from ..utils.type_utils import (
    is_list_type, is_dataframe_type, is_composite_type, 
    has_all_list_fields, get_composite_fields, is_optional_type,
    get_optional_inner_type, is_tuple_type, is_scalar_type, 
    has_any_non_list_fields, get_args_safe
)


class ProcessingMode(Enum):
    """Processing modes describing input → output data flow patterns."""
    RECORD_TO_RECORD = "record_to_record"
    RECORD_TO_BATCH = "record_to_batch" 
    BATCH_TO_BATCH = "batch_to_batch"


def determine_processing_mode(
    type_hints: Dict[str, Any], 
    signature: inspect.Signature,
    return_type_hint: Any = None
) -> ProcessingMode:
    """
    Determine processing mode based on function signature and return type.
    
    Args:
        type_hints: Function type hints  
        signature: Function signature
        return_type_hint: Return type hint for output mode detection
        
    Returns:
        ProcessingMode describing the data flow pattern
    """
    is_record_input = _is_record_input(type_hints, signature)
    is_batch_output = _is_batch_output(return_type_hint) if return_type_hint else False
    
    if is_record_input:
        if is_batch_output:
            return ProcessingMode.RECORD_TO_BATCH
        else:
            return ProcessingMode.RECORD_TO_RECORD
    else:
        # Batch input always produces batch output (collections stay as columns)
        return ProcessingMode.BATCH_TO_BATCH


def _is_record_input(
    type_hints: Dict[str, Any], 
    signature: inspect.Signature
) -> bool:
    """
    Determine if input processing should be record-by-record.
    
    Record processing if ANY parameter is:
    - Scalar type OR
    - Composite type with ANY non-list field
    
    Args:
        type_hints: Function type hints
        signature: Function signature
        
    Returns:
        True if record-by-record processing, False if batch processing
    """
    param_types = {
        name: type_hints[name] 
        for name in signature.parameters 
        if name in type_hints
    }
    
    # Check each parameter type
    for param_name, param_type in param_types.items():
        
        # DataFrame parameters always trigger batch processing
        if is_dataframe_type(param_type):
            return False
        
        # Scalar parameters trigger record processing
        if is_scalar_type(param_type):
            return True
        
        # Composite types with any non-list fields trigger record processing
        if is_composite_type(param_type) and has_any_non_list_fields(param_type):
            return True
    
    # If we get here, all parameters are either:
    # - List types
    # - Composite types with all list fields
    # This means batch processing
    return False


def _is_batch_output(return_type_hint: Any) -> bool:
    """
    Determine if output should be treated as batch (collection/list column).
    
    Batch output if return type is:
    - List type OR
    - Composite type with all list fields OR 
    - DataFrame type
    
    Args:
        return_type_hint: Return type hint
        
    Returns:
        True if batch output, False if record output
    """
    if return_type_hint is None:
        return False
    
    # Handle tuple return types (success, error) - use success type
    if hasattr(return_type_hint, '__origin__') and return_type_hint.__origin__ is tuple:
        args = get_args_safe(return_type_hint)
        if args:
            return_type_hint = args[0]  # Use success type for mode detection
    
    # List return types indicate batch output (collection as column)
    if is_list_type(return_type_hint):
        return True
    
    # Composite types with all list fields indicate batch output
    if is_composite_type(return_type_hint) and has_all_list_fields(return_type_hint):
        return True
    
    # DataFrame types indicate batch output
    if is_dataframe_type(return_type_hint):
        return True
    
    # Everything else is record output
    return False


# Helper functions for backward compatibility and readability
def is_record_input_processing(mode: ProcessingMode) -> bool:
    """Check if processing mode uses record-by-record input."""
    return mode in (ProcessingMode.RECORD_TO_RECORD, ProcessingMode.RECORD_TO_BATCH)


def is_batch_input_processing(mode: ProcessingMode) -> bool:
    """Check if processing mode uses batch input."""
    return mode == ProcessingMode.BATCH_TO_BATCH


def is_record_output(mode: ProcessingMode) -> bool:
    """Check if processing mode produces record output."""
    return mode == ProcessingMode.RECORD_TO_RECORD


def is_batch_output(mode: ProcessingMode) -> bool:
    """Check if processing mode produces batch output."""
    return mode in (ProcessingMode.RECORD_TO_BATCH, ProcessingMode.BATCH_TO_BATCH)


def get_processing_reason(
    mode: ProcessingMode,
    type_hints: Dict[str, Any], 
    signature: inspect.Signature,
    return_type_hint: Any = None
) -> str:
    """
    Get a description of why this processing mode was selected.
    
    Args:
        mode: Determined processing mode
        type_hints: Function type hints
        signature: Function signature
        return_type_hint: Return type hint
        
    Returns:
        Human-readable explanation
    """
    input_reason = _get_input_reason(mode, type_hints, signature)
    output_reason = _get_output_reason(mode, return_type_hint)
    
    return f"Input: {input_reason}; Output: {output_reason}"


def _get_input_reason(
    mode: ProcessingMode,
    type_hints: Dict[str, Any], 
    signature: inspect.Signature
) -> str:
    """Get reason for input processing choice."""
    if is_record_input_processing(mode):
        return _get_record_input_reason(type_hints, signature)
    else:
        return _get_batch_input_reason(type_hints, signature)


def _get_output_reason(mode: ProcessingMode, return_type_hint: Any = None) -> str:
    """Get reason for output processing choice."""
    if is_batch_output(mode):
        return _get_batch_output_reason(return_type_hint)
    else:
        return "scalar/composite return type → record output"


def _get_record_input_reason(
    type_hints: Dict[str, Any], 
    signature: inspect.Signature
) -> str:
    """Get reason for record input processing."""
    param_types = {
        name: type_hints[name] 
        for name in signature.parameters 
        if name in type_hints
    }
    
    # Check for scalar parameters
    scalar_params = [
        name for name, param_type in param_types.items() 
        if is_scalar_type(param_type)
    ]
    
    if scalar_params:
        return f"scalar parameters ({', '.join(scalar_params)}) → record input"
    
    # Check for composite types with non-list fields
    mixed_composite_params = [
        name for name, param_type in param_types.items()
        if is_composite_type(param_type) and has_any_non_list_fields(param_type)
    ]
    
    if mixed_composite_params:
        return f"composite types with non-list fields ({', '.join(mixed_composite_params)}) → record input"
    
    return "record input processing"


def _get_batch_input_reason(
    type_hints: Dict[str, Any], 
    signature: inspect.Signature
) -> str:
    """Get reason for batch input processing."""
    param_types = {
        name: type_hints[name] 
        for name in signature.parameters 
        if name in type_hints
    }
    
    # Check for DataFrame
    dataframe_params = [
        name for name, param_type in param_types.items()
        if is_dataframe_type(param_type)
    ]
    
    if dataframe_params:
        return f"DataFrame parameter ({', '.join(dataframe_params)}) → batch input"
    
    # Check for all-list composite types
    all_list_composite_params = [
        name for name, param_type in param_types.items()
        if is_composite_type(param_type) and has_all_list_fields(param_type)
    ]
    
    if all_list_composite_params:
        return f"composite types with all list fields ({', '.join(all_list_composite_params)}) → batch input"
    
    # Must be all list parameters
    list_params = [
        name for name, param_type in param_types.items() 
        if is_list_type(param_type)
    ]
    
    if list_params:
        return f"list-only parameters ({', '.join(list_params)}) → batch input"
    
    return "batch input processing"


def _get_batch_output_reason(return_type_hint: Any = None) -> str:
    """Get reason for batch output processing."""
    if return_type_hint is None:
        return "batch output"
    
    # Handle tuple return types
    if hasattr(return_type_hint, '__origin__') and return_type_hint.__origin__ is tuple:
        args = get_args_safe(return_type_hint)
        if args:
            return_type_hint = args[0]
    
    if is_list_type(return_type_hint):
        return "List return type → batch output (collection as column)"
    elif is_dataframe_type(return_type_hint):
        return "DataFrame return type → batch output"
    elif is_composite_type(return_type_hint) and has_all_list_fields(return_type_hint):
        return "composite type with all list fields → batch output"
    else:
        return "batch output"