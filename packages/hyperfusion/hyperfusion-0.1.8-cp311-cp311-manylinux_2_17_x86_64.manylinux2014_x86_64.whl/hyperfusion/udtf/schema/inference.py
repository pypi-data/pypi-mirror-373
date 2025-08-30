"""Schema inference from Python type annotations."""

import inspect
from typing import Dict, Any, Tuple, Optional

try:
    import pyarrow as pa
except ImportError:
    pa = None

from ..utils.type_utils import (
    is_optional_type, get_optional_inner_type, is_list_type, is_tuple_type,
    is_composite_type, has_all_list_fields, get_args_safe, is_schema_inferrable_type,
    requires_explicit_schema
)
from ..utils.arrow_utils import create_arrow_schema
from ..schema.mapping import create_arrow_field_from_python
from ..error_handling.exceptions import SchemaError
from ..error_handling.error_schemas import create_default_error_schema


def infer_input_schema(type_hints: Dict[str, Any], signature: inspect.Signature) -> 'pa.Schema':
    """
    Infer input schema from function parameter type hints.
    
    Args:
        type_hints: Function type hints
        signature: Function signature
        
    Returns:
        Arrow schema for input parameters
        
    Raises:
        SchemaError: If schema cannot be inferred
    """
    if not pa:
        raise SchemaError("PyArrow is required but not installed")
    
    fields = []
    
    for param_name in signature.parameters:
        if param_name not in type_hints:
            raise SchemaError(f"Missing type hint for parameter '{param_name}'")
        
        param_type = type_hints[param_name]
        
        # DataFrame types require explicit schema
        from ..utils.type_utils import is_dataframe_type
        if is_dataframe_type(param_type):
            raise SchemaError(f"DataFrame parameter '{param_name}' requires explicit input schema")
        
        try:
            field = create_arrow_field_from_python(param_name, param_type)
            fields.append(field)
        except Exception as e:
            raise SchemaError(f"Cannot infer schema for parameter '{param_name}': {e}")
    
    return create_arrow_schema(fields)


def infer_output_schema(return_type: Any, input_schema: 'pa.Schema') -> Tuple[Optional['pa.Schema'], Optional['pa.Schema']]:
    """
    Infer output and error schemas from return type annotation.
    
    Args:
        return_type: Function return type hint
        input_schema: Input schema for default error handling
        
    Returns:
        Tuple of (output_schema, error_schema)
        
    Raises:
        SchemaError: If schema cannot be inferred
    """
    if not pa:
        raise SchemaError("PyArrow is required but not installed")
    
    # Handle tuple return type (success, error)
    if is_tuple_type(return_type):
        args = get_args_safe(return_type)
        if len(args) != 2:
            raise SchemaError(f"Tuple return type must have exactly 2 elements, got {len(args)}")
        
        success_type, error_type = args
        
        # Infer success schema
        success_schema = None
        if success_type is not type(None):
            success_schema = _infer_single_output_schema(success_type)
        
        # Infer error schema
        error_schema = None
        if error_type is not type(None):
            error_schema = _infer_error_schema(error_type)
        else:
            error_schema = create_default_error_schema(input_schema)
        
        return success_schema, error_schema
    
    # Single return type
    else:
        success_schema = _infer_single_output_schema(return_type)
        error_schema = create_default_error_schema(input_schema)
        return success_schema, error_schema


def _infer_single_output_schema(return_type: Any) -> Optional['pa.Schema']:
    """Infer schema for a single output type."""
    # Handle None type
    if return_type is type(None):
        return None
    
    # Types that require explicit schema
    if requires_explicit_schema(return_type):
        raise SchemaError(f"Return type {return_type} requires explicit output schema")
    
    # Schema-inferrable types
    if is_schema_inferrable_type(return_type):
        return _infer_composite_output_schema(return_type)
    
    # Handle List[CompositeType] - extract the composite type and infer its schema
    if is_list_type(return_type):
        args = get_args_safe(return_type)
        if args and is_schema_inferrable_type(args[0]):
            # List of composite types - infer schema from the element type
            return _infer_composite_output_schema(args[0])
    
    raise SchemaError(f"Cannot infer output schema for return type {return_type}")


def _infer_composite_output_schema(composite_type: Any) -> 'pa.Schema':
    """Infer schema for composite types (dataclass, NamedTuple, TypedDict)."""
    from ..utils.type_utils import get_composite_fields
    
    fields = get_composite_fields(composite_type)
    if not fields:
        raise SchemaError(f"Composite type {composite_type} has no fields")
    
    # Determine if this represents a RecordBatch schema or record schema
    if has_all_list_fields(composite_type):
        # All fields are lists - interpret as RecordBatch schema
        arrow_fields = []
        for field_name, field_type in fields.items():
            # Extract list element type
            if not is_list_type(field_type):
                raise SchemaError(f"Expected list type for field '{field_name}'")
            
            args = get_args_safe(field_type)
            if not args:
                raise SchemaError(f"List type for field '{field_name}' missing element type")
            
            element_type = args[0]
            field = create_arrow_field_from_python(field_name, element_type)
            arrow_fields.append(field)
        
        return create_arrow_schema(arrow_fields)
    
    else:
        # Some fields are non-list - interpret as record schema
        arrow_fields = []
        for field_name, field_type in fields.items():
            field = create_arrow_field_from_python(field_name, field_type)
            arrow_fields.append(field)
        
        return create_arrow_schema(arrow_fields)


def _infer_error_schema(error_type: Any) -> 'pa.Schema':
    """Infer schema for custom error type."""
    if not is_schema_inferrable_type(error_type):
        raise SchemaError(f"Error type {error_type} is not schema-inferrable")
    
    # Infer base error schema
    base_schema = _infer_composite_output_schema(error_type)
    
    # Add exception field
    from ..utils.arrow_utils import create_arrow_field
    exception_field = create_arrow_field("exception", pa.string(), nullable=True)
    
    # Combine fields
    all_fields = list(base_schema) + [exception_field]
    return create_arrow_schema(all_fields)


def is_record_processing_mode(type_hints: Dict[str, Any]) -> bool:
    """
    Determine if function should use record-by-record processing.
    
    Args:
        type_hints: Function type hints
        
    Returns:
        True if record processing, False if batch processing
    """
    from ..utils.type_utils import is_scalar_type, has_any_non_list_fields, is_dataframe_type
    
    for param_name, param_type in type_hints.items():
        if param_name == 'return':
            continue
        
        # DataFrame parameters trigger batch processing
        if is_dataframe_type(param_type):
            return False
        
        # Scalar parameters trigger record processing
        if is_scalar_type(param_type):
            return True
        
        # Composite types with any non-list fields trigger record processing
        if is_composite_type(param_type) and has_any_non_list_fields(param_type):
            return True
    
    # Default to batch processing for all-list parameters
    return False