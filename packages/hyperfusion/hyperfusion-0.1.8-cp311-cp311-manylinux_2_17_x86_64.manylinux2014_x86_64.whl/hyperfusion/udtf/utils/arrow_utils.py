"""Arrow utility functions for schema and field creation."""

from typing import List, Optional

try:
    import pyarrow as pa
except ImportError:
    pa = None

from ..error_handling.exceptions import UDTFError


def create_arrow_field(name: str, arrow_type: 'pa.DataType', nullable: bool = True) -> 'pa.Field':
    """Create an Arrow field with the given name, type, and nullability."""
    if not pa:
        raise UDTFError("PyArrow is required but not installed")
    
    return pa.field(name, arrow_type, nullable=nullable)


def create_arrow_schema(fields: List['pa.Field']) -> 'pa.Schema':
    """Create an Arrow schema from a list of fields."""
    if not pa:
        raise UDTFError("PyArrow is required but not installed")
    
    return pa.schema(fields)


def get_arrow_type_size(arrow_type: 'pa.DataType') -> Optional[int]:
    """Get the size in bytes of an Arrow type, if applicable."""
    if not pa:
        return None
    
    if isinstance(arrow_type, (pa.Int8Type, pa.UInt8Type)):
        return 1
    elif isinstance(arrow_type, (pa.Int16Type, pa.UInt16Type)):
        return 2
    elif isinstance(arrow_type, (pa.Int32Type, pa.UInt32Type, pa.FloatType)):
        return 4
    elif isinstance(arrow_type, (pa.Int64Type, pa.UInt64Type, pa.DoubleType)):
        return 8
    
    return None


def is_numeric_type(arrow_type: 'pa.DataType') -> bool:
    """Check if an Arrow type is numeric."""
    if not pa:
        return False
    
    return pa.types.is_integer(arrow_type) or pa.types.is_floating(arrow_type)


def is_integer_type(arrow_type: 'pa.DataType') -> bool:
    """Check if an Arrow type is an integer type."""
    if not pa:
        return False
    
    return pa.types.is_integer(arrow_type)


def is_float_type(arrow_type: 'pa.DataType') -> bool:
    """Check if an Arrow type is a floating point type."""
    if not pa:
        return False
    
    return pa.types.is_floating(arrow_type)


def can_cast_type(from_type: 'pa.DataType', to_type: 'pa.DataType') -> bool:
    """Check if one Arrow type can be cast to another according to the spec."""
    if not pa:
        return False
    
    # Same types are always compatible
    if from_type.equals(to_type):
        return True
    
    # Use PyArrow's built-in casting compatibility check for basic types
    try:
        if not (pa.types.is_struct(from_type) or pa.types.is_list(from_type) or pa.types.is_map(from_type)):
            return pa.compute.can_cast(from_type, to_type)
    except:
        pass
    
    # Handle complex types recursively
    if pa.types.is_struct(from_type) and pa.types.is_struct(to_type):
        return _can_cast_struct_type(from_type, to_type)
    
    if pa.types.is_list(from_type) and pa.types.is_list(to_type):
        return _can_cast_list_type(from_type, to_type)
    
    if pa.types.is_map(from_type) and pa.types.is_map(to_type):
        return _can_cast_map_type(from_type, to_type)
    
    # Fall back to basic type checking for scalar types
    if pa.types.is_integer(from_type) and pa.types.is_integer(to_type):
        # Allow integer widening: int32 -> int64, etc.
        from_bits = _get_type_bit_width(from_type)
        to_bits = _get_type_bit_width(to_type)
        return from_bits <= to_bits if from_bits and to_bits else False
    
    if pa.types.is_floating(from_type) and pa.types.is_floating(to_type):
        # Allow float widening: float32 -> float64
        return str(from_type) == "float" and str(to_type) == "double"
    
    # String and boolean types are compatible with themselves
    return (pa.types.is_string(from_type) and pa.types.is_string(to_type)) or \
           (pa.types.is_boolean(from_type) and pa.types.is_boolean(to_type))


def _can_cast_struct_type(from_struct: 'pa.StructType', to_struct: 'pa.StructType') -> bool:
    """Check if struct types are compatible."""
    if len(from_struct) != len(to_struct):
        return False
    
    # Create field mappings by name
    from_fields = {field.name: field for field in from_struct}
    to_fields = {field.name: field for field in to_struct}
    
    # Check all fields match by name and can be cast
    for field_name in from_fields:
        if field_name not in to_fields:
            return False
        
        from_field = from_fields[field_name]
        to_field = to_fields[field_name]
        
        # Check nullability - should match exactly for validation
        if from_field.nullable != to_field.nullable:
            return False
        
        # Check field type compatibility recursively
        if not can_cast_type(from_field.type, to_field.type):
            return False
    
    return True


def _can_cast_list_type(from_list: 'pa.ListType', to_list: 'pa.ListType') -> bool:
    """Check if list types are compatible."""
    return can_cast_type(from_list.value_type, to_list.value_type)


def _can_cast_map_type(from_map: 'pa.MapType', to_map: 'pa.MapType') -> bool:
    """Check if map types are compatible."""
    # Key types must match exactly
    if not from_map.key_type.equals(to_map.key_type):
        return False
    
    # Value types can be cast
    return can_cast_type(from_map.item_type, to_map.item_type)


def _get_type_bit_width(arrow_type: 'pa.DataType') -> int:
    """Get bit width of an Arrow type."""
    if not pa:
        return None
    
    type_str = str(arrow_type)
    if "int8" in type_str:
        return 8
    elif "int16" in type_str:
        return 16
    elif "int32" in type_str:
        return 32
    elif "int64" in type_str:
        return 64
    return None


def extract_list_value_type(list_type: 'pa.ListType') -> 'pa.DataType':
    """Extract the value type from a list type."""
    if not pa or not isinstance(list_type, pa.ListType):
        raise UDTFError("Expected Arrow list type")
    
    return list_type.value_type


def extract_map_types(map_type: 'pa.MapType') -> tuple['pa.DataType', 'pa.DataType']:
    """Extract key and value types from a map type."""
    if not pa or not isinstance(map_type, pa.MapType):
        raise UDTFError("Expected Arrow map type")
    
    return map_type.key_type, map_type.item_type


def extract_struct_fields(struct_type: 'pa.StructType') -> List['pa.Field']:
    """Extract fields from a struct type."""
    if not pa or not isinstance(struct_type, pa.StructType):
        raise UDTFError("Expected Arrow struct type")
    
    return list(struct_type)