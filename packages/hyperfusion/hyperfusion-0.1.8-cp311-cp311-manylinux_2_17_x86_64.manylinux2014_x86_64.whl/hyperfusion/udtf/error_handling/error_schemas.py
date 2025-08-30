"""Error schema creation and management."""

from typing import Optional

try:
    import pyarrow as pa
except ImportError:
    pa = None

# Direct PyArrow usage to avoid circular imports
from ..error_handling.exceptions import SchemaError


def create_default_error_schema(input_schema: 'pa.Schema') -> 'pa.Schema':
    """
    Create the default error schema with all input fields plus exception field.
    
    Args:
        input_schema: The input schema to preserve in error records
        
    Returns:
        Error schema with input fields + exception field
    """
    if not pa:
        raise SchemaError("PyArrow is required but not installed")
    
    # Copy all input fields
    error_fields = list(input_schema)
    
    # Add exception field
    exception_field = pa.field("exception", pa.string(), nullable=True)
    error_fields.append(exception_field)
    
    return pa.schema(error_fields)


def create_custom_error_schema(base_schema: 'pa.Schema') -> 'pa.Schema':
    """
    Create a custom error schema by adding exception field to base schema.
    
    Args:
        base_schema: The base error schema inferred from error type
        
    Returns:
        Error schema with base fields + exception field
    """
    if not pa:
        raise SchemaError("PyArrow is required but not installed")
    
    # Check if exception field already exists
    existing_names = {field.name for field in base_schema}
    if "exception" in existing_names:
        raise SchemaError("Error schema cannot contain field named 'exception' - this field is added automatically")
    
    # Copy base fields
    error_fields = list(base_schema)
    
    # Add exception field
    exception_field = pa.field("exception", pa.string(), nullable=True)
    error_fields.append(exception_field)
    
    return pa.schema(error_fields)


def create_batch_error_schema(input_schema: 'pa.Schema') -> 'pa.Schema':
    """
    Create error schema for batch processing failures.
    
    In batch mode, if an exception occurs, the entire batch fails and is written
    to error output with an exception column.
    
    Args:
        input_schema: The input schema to preserve in error records
        
    Returns:
        Error schema identical to input schema + exception field
    """
    # For batch processing, error schema is same as default
    return create_default_error_schema(input_schema)


def add_exception_to_record(
    record: dict, 
    exception: Exception,
    error_schema: 'pa.Schema'
) -> dict:
    """
    Add exception information to an error record.
    
    Args:
        record: The error record data
        exception: The exception that occurred
        error_schema: The error schema to validate against
        
    Returns:
        Record with exception field added
    """
    # Validate exception field exists in schema
    schema_names = {field.name for field in error_schema}
    if "exception" not in schema_names:
        raise SchemaError("Error schema must contain 'exception' field")
    
    # Add exception message
    error_record = record.copy()
    error_record["exception"] = str(exception)
    
    return error_record


def validate_error_schema(error_schema: 'pa.Schema') -> None:
    """
    Validate that an error schema is properly formed.
    
    Args:
        error_schema: The error schema to validate
        
    Raises:
        SchemaError: If schema is invalid
    """
    if not pa:
        raise SchemaError("PyArrow is required but not installed")
    
    if not error_schema:
        raise SchemaError("Error schema cannot be None")
    
    # Check that exception field exists
    field_names = {field.name for field in error_schema}
    if "exception" not in field_names:
        raise SchemaError("Error schema must contain 'exception' field")
    
    # Check exception field type
    exception_field = next(field for field in error_schema if field.name == "exception")
    if not isinstance(exception_field.type, pa.StringType):
        raise SchemaError("Exception field must be of string type")
    
    if not exception_field.nullable:
        raise SchemaError("Exception field must be nullable")