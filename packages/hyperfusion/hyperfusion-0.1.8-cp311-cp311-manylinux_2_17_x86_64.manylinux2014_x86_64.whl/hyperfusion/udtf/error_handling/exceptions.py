"""Custom exceptions for UDTF processing."""


class UDTFError(Exception):
    """Base exception for UDTF-related errors."""
    pass


class SchemaError(UDTFError):
    """Exception raised for schema-related errors."""
    pass


class ValidationError(UDTFError):
    """Exception raised for validation errors."""
    pass


class TypeMappingError(UDTFError):
    """Exception raised for type mapping errors."""
    pass


class ProcessingError(UDTFError):
    """Exception raised during function processing."""
    pass


class ConversionError(UDTFError):
    """Exception raised during data conversion."""
    pass