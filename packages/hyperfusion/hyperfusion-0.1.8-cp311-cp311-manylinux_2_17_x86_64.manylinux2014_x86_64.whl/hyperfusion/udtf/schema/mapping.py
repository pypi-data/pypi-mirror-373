"""Type mapping between Python types and Arrow types."""

from typing import Any

try:
    import pyarrow as pa
except ImportError:
    pa = None

from ..utils.type_utils import (
    is_optional_type, get_optional_inner_type, is_list_type, is_dict_type,
    is_composite_type, is_scalar_type, get_composite_fields, get_args_safe
)
from ..utils.arrow_utils import create_arrow_field
from ..error_handling.exceptions import TypeMappingError


def map_python_to_arrow_type(python_type: Any) -> 'pa.DataType':
    """
    Map a Python type to an Arrow type according to the specification.
    
    Args:
        python_type: The Python type to map
        
    Returns:
        The corresponding Arrow type
        
    Raises:
        TypeMappingError: If the type cannot be mapped
    """
    if not pa:
        raise TypeMappingError("PyArrow is required but not installed")
    
    # Handle Optional types by extracting inner type
    inner_type = get_optional_inner_type(python_type)
    
    # Scalar types
    if inner_type is int:
        return pa.int64()
    elif inner_type is float:
        return pa.float64()
    elif inner_type is str:
        return pa.string()
    elif inner_type is bool:
        return pa.bool_()
    
    # List types
    elif is_list_type(inner_type):
        args = get_args_safe(inner_type)
        if not args:
            raise TypeMappingError(f"List type {inner_type} missing type argument")
        
        element_type = map_python_to_arrow_type(args[0])
        return pa.list_(element_type)
    
    # Dict types (Map in Arrow)
    elif is_dict_type(inner_type):
        args = get_args_safe(inner_type)
        if len(args) != 2:
            raise TypeMappingError(f"Dict type {inner_type} must have exactly 2 type arguments")
        
        key_type, value_type = args
        if key_type is not str:
            raise TypeMappingError(f"Dict keys must be str type, got {key_type}")
        
        arrow_key_type = pa.string()
        arrow_value_type = map_python_to_arrow_type(value_type)
        return pa.map_(arrow_key_type, arrow_value_type)
    
    # Composite types (struct in Arrow)
    elif is_composite_type(inner_type):
        fields = get_composite_fields(inner_type)
        arrow_fields = []
        
        for field_name, field_type in fields.items():
            # Determine nullability based on whether the field type is Optional
            field_nullable = is_optional_type(field_type)
            arrow_field_type = map_python_to_arrow_type(field_type)
            arrow_field = create_arrow_field(field_name, arrow_field_type, field_nullable)
            arrow_fields.append(arrow_field)
        
        return pa.struct(arrow_fields)
    
    else:
        raise TypeMappingError(f"Unsupported type: {python_type}")


def create_arrow_field_from_python(name: str, python_type: Any) -> 'pa.Field':
    """
    Create an Arrow field from a Python type.
    
    Args:
        name: Field name
        python_type: Python type annotation
        
    Returns:
        Arrow field with appropriate nullability
    """
    # Determine nullability based on whether the type is Optional
    nullable = is_optional_type(python_type)
    arrow_type = map_python_to_arrow_type(python_type)
    return create_arrow_field(name, arrow_type, nullable)


def is_compatible_arrow_type(python_type: Any, arrow_type: 'pa.DataType', nullable: bool) -> bool:
    """
    Check if an Arrow type is compatible with a Python type.
    
    Args:
        python_type: The Python type
        arrow_type: The Arrow type
        nullable: Whether the Arrow field is nullable
        
    Returns:
        True if compatible, False otherwise
    """
    try:
        expected_arrow_type = map_python_to_arrow_type(python_type)
        expected_nullable = is_optional_type(python_type)
        
        # Check nullability matches exactly
        if nullable != expected_nullable:
            return False
        
        # Check type compatibility
        return _are_arrow_types_compatible(expected_arrow_type, arrow_type)
    
    except TypeMappingError:
        return False


def _are_arrow_types_compatible(expected: 'pa.DataType', actual: 'pa.DataType') -> bool:
    """Check if two Arrow types are compatible (allowing widening)."""
    if not pa:
        return False
    
    # Exact match
    if expected.equals(actual):
        return True
    
    # Numeric widening rules using modern PyArrow API
    if pa.types.is_integer(expected) and pa.types.is_integer(actual):
        return _can_widen_integer(expected, actual)
    
    if pa.types.is_floating(expected) and pa.types.is_floating(actual):
        return _can_widen_float(expected, actual)
    
    # List types
    if pa.types.is_list(expected) and pa.types.is_list(actual):
        return _are_arrow_types_compatible(expected.value_type, actual.value_type)
    
    # Map types
    if pa.types.is_map(expected) and pa.types.is_map(actual):
        key_compatible = _are_arrow_types_compatible(expected.key_type, actual.key_type)
        value_compatible = _are_arrow_types_compatible(expected.item_type, actual.item_type)
        return key_compatible and value_compatible
    
    # Struct types
    if pa.types.is_struct(expected) and pa.types.is_struct(actual):
        return _are_struct_types_compatible(expected, actual)
    
    return False


def _can_widen_integer(from_type: 'pa.DataType', to_type: 'pa.DataType') -> bool:
    """Check if integer type can be widened."""
    type_hierarchy = [
        pa.int8(), pa.int16(), pa.int32(), pa.int64()
    ]
    
    try:
        from_idx = next(i for i, t in enumerate(type_hierarchy) if from_type.equals(t))
        to_idx = next(i for i, t in enumerate(type_hierarchy) if to_type.equals(t))
        return from_idx <= to_idx
    except StopIteration:
        return False


def _can_widen_float(from_type: 'pa.DataType', to_type: 'pa.DataType') -> bool:
    """Check if float type can be widened."""
    if from_type.equals(pa.float32()) and to_type.equals(pa.float64()):
        return True
    return from_type.equals(to_type)


def _are_struct_types_compatible(expected: 'pa.StructType', actual: 'pa.StructType') -> bool:
    """Check if struct types are compatible."""
    # Must have same number of fields
    if len(expected) != len(actual):
        return False
    
    # Create field name mappings
    expected_fields = {field.name: field for field in expected}
    actual_fields = {field.name: field for field in actual}
    
    # Must have same field names
    if set(expected_fields.keys()) != set(actual_fields.keys()):
        return False
    
    # Check each field compatibility
    for field_name in expected_fields:
        expected_field = expected_fields[field_name]
        actual_field = actual_fields[field_name]
        
        # Nullability must match exactly
        if expected_field.nullable != actual_field.nullable:
            return False
        
        # Types must be compatible
        if not _are_arrow_types_compatible(expected_field.type, actual_field.type):
            return False
    
    return True