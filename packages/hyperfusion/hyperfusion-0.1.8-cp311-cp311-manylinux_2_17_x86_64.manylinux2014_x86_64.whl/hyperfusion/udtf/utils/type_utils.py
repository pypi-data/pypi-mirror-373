"""Type utility functions for analyzing Python types."""

import sys
from typing import Any, Union, get_origin, get_args
from dataclasses import is_dataclass

try:
    import pandas as pd
except ImportError:
    pd = None

try:
    import polars as pl
except ImportError:
    pl = None

try:
    import pyarrow as pa
except ImportError:
    pa = None


def get_origin_safe(tp: Any) -> Any:
    """Get the origin of a type annotation, handling version differences."""
    if sys.version_info >= (3, 8):
        return get_origin(tp)
    else:
        return getattr(tp, '__origin__', None)


def get_args_safe(tp: Any) -> tuple:
    """Get the args of a type annotation, handling version differences."""
    if sys.version_info >= (3, 8):
        return get_args(tp)
    else:
        return getattr(tp, '__args__', ())


def is_optional_type(tp: Any) -> bool:
    """Check if a type is Optional[T] or Union[T, None]."""
    origin = get_origin_safe(tp)
    if origin is Union:
        args = get_args_safe(tp)
        return len(args) == 2 and type(None) in args
    return False


def get_optional_inner_type(tp: Any) -> Any:
    """Get the inner type from Optional[T] or Union[T, None]."""
    if is_optional_type(tp):
        args = get_args_safe(tp)
        return args[0] if args[1] is type(None) else args[1]
    return tp


def is_list_type(tp: Any) -> bool:
    """Check if a type is List[T]."""
    origin = get_origin_safe(tp)
    return origin is list


def is_dict_type(tp: Any) -> bool:
    """Check if a type is Dict[K, V]."""
    origin = get_origin_safe(tp)
    return origin is dict


def is_tuple_type(tp: Any) -> bool:
    """Check if a type is Tuple[...] or tuple."""
    if tp is tuple:
        return True
    origin = get_origin_safe(tp)
    return origin is tuple


def is_dataframe_type(tp: Any) -> bool:
    """Check if a type is a DataFrame type (pandas, polars, or pyarrow)."""
    if pd and tp is pd.DataFrame:
        return True
    if pl and tp is pl.DataFrame:
        return True
    if pa and tp is pa.Table:
        return True
    
    # Handle string annotations for DataFrames
    if isinstance(tp, str):
        return tp in ['pd.DataFrame', 'pl.DataFrame', 'pa.Table', 'pandas.DataFrame', 'polars.DataFrame', 'pyarrow.Table']
    
    return False


def is_composite_type(tp: Any) -> bool:
    """Check if a type is a composite type (dataclass, NamedTuple, TypedDict)."""
    # Handle Optional types
    inner_type = get_optional_inner_type(tp)
    
    # Check for dataclass
    if is_dataclass(inner_type):
        return True
    
    # Check for NamedTuple
    if hasattr(inner_type, '_fields') and hasattr(inner_type, '__annotations__'):
        return True
    
    # Check for TypedDict
    if hasattr(inner_type, '__annotations__') and hasattr(inner_type, '__total__'):
        return True
    
    return False


def is_scalar_type(tp: Any) -> bool:
    """Check if a type is a scalar type (int, float, str, bool)."""
    scalar_types = (int, float, str, bool)
    inner_type = get_optional_inner_type(tp)
    return inner_type in scalar_types


def get_composite_fields(tp: Any) -> dict:
    """Get field information from a composite type."""
    inner_type = get_optional_inner_type(tp)
    
    # Dataclass
    if is_dataclass(inner_type):
        import dataclasses
        fields = dataclasses.fields(inner_type)
        return {field.name: field.type for field in fields}
    
    # NamedTuple
    if hasattr(inner_type, '_field_types'):
        return inner_type._field_types
    elif hasattr(inner_type, '__annotations__'):
        # Modern NamedTuple with annotations
        return inner_type.__annotations__
    
    # TypedDict
    if hasattr(inner_type, '__annotations__'):
        return inner_type.__annotations__
    
    return {}


def has_all_list_fields(tp: Any) -> bool:
    """Check if a composite type has all list fields."""
    fields = get_composite_fields(tp)
    if not fields:
        return False
    
    def is_list_field(field_type):
        """Check if a field type is a list or dict (collection), possibly wrapped in Optional."""
        # Unwrap Optional to check the inner type
        inner_type = get_optional_inner_type(field_type)
        return is_list_type(inner_type) or is_dict_type(inner_type)
    
    return all(is_list_field(field_type) for field_type in fields.values())


def has_any_non_list_fields(tp: Any) -> bool:
    """Check if a composite type has any non-list fields."""
    fields = get_composite_fields(tp)
    if not fields:
        return False
    
    def is_list_field(field_type):
        """Check if a field type is a list or dict (collection), possibly wrapped in Optional."""
        # Unwrap Optional to check the inner type
        inner_type = get_optional_inner_type(field_type)
        return is_list_type(inner_type) or is_dict_type(inner_type)
    
    return any(not is_list_field(field_type) for field_type in fields.values())


def is_schema_inferrable_type(tp: Any) -> bool:
    """Check if a type allows automatic schema inference."""
    return is_composite_type(tp)


def requires_explicit_schema(tp: Any) -> bool:
    """Check if a type requires explicit schema provision."""
    inner_type = get_optional_inner_type(tp)
    
    # Scalar types
    if is_scalar_type(tp):
        return True
    
    # DataFrame types  
    if is_dataframe_type(inner_type):
        return True
    
    # List of scalars
    if is_list_type(inner_type):
        args = get_args_safe(inner_type)
        if args and is_scalar_type(args[0]):
            return True
    
    return False