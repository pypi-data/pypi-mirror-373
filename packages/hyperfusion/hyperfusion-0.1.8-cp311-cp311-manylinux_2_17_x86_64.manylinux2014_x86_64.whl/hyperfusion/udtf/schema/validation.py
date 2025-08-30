"""Schema validation and compatibility checking."""

from typing import Set

try:
    import pyarrow as pa
except ImportError:
    pa = None

from ..utils.arrow_utils import can_cast_type
from ..error_handling.exceptions import ValidationError


def validate_schema_compatibility(
    explicit_schema: 'pa.Schema', 
    inferred_schema: 'pa.Schema', 
    schema_type: str
) -> None:
    """
    Validate that an explicit schema is compatible with an inferred schema.
    
    Args:
        explicit_schema: The explicitly provided schema
        inferred_schema: The schema inferred from type hints
        schema_type: Type of schema (for error messages): "input", "output", or "error"
        
    Raises:
        ValidationError: If schemas are incompatible
    """
    if not pa:
        raise ValidationError("PyArrow is required but not installed")
    
    # Check field name compatibility
    _validate_field_names(explicit_schema, inferred_schema, schema_type)
    
    # Check field type compatibility
    _validate_field_types(explicit_schema, inferred_schema, schema_type)


def _validate_field_names(
    explicit_schema: 'pa.Schema', 
    inferred_schema: 'pa.Schema', 
    schema_type: str
) -> None:
    """Validate that field names match between schemas."""
    explicit_names = set(field.name for field in explicit_schema)
    inferred_names = set(field.name for field in inferred_schema)
    
    if explicit_names != inferred_names:
        missing_in_explicit = inferred_names - explicit_names
        extra_in_explicit = explicit_names - inferred_names
        
        error_parts = []
        if missing_in_explicit:
            error_parts.append(f"missing fields {sorted(missing_in_explicit)}")
        if extra_in_explicit:
            error_parts.append(f"extra fields {sorted(extra_in_explicit)}")
        
        raise ValidationError(
            f"Field name mismatch in {schema_type} schema: {', '.join(error_parts)}. "
            f"Expected fields: {sorted(inferred_names)}"
        )


def _validate_field_types(
    explicit_schema: 'pa.Schema', 
    inferred_schema: 'pa.Schema', 
    schema_type: str
) -> None:
    """Validate that field types are compatible between schemas."""
    # Create field mappings by name
    explicit_fields = {field.name: field for field in explicit_schema}
    inferred_fields = {field.name: field for field in inferred_schema}
    
    for field_name in explicit_fields:
        explicit_field = explicit_fields[field_name]
        inferred_field = inferred_fields[field_name]
        
        # Validate nullability matches exactly
        if explicit_field.nullable != inferred_field.nullable:
            raise ValidationError(
                f"Cannot change nullability: expected nullable={inferred_field.nullable} "
                f"for field '{field_name}', got nullable={explicit_field.nullable}"
            )
        
        # Validate type compatibility
        if not _are_types_compatible(inferred_field.type, explicit_field.type):
            raise ValidationError(
                f"Cannot map type {inferred_field.type} to {explicit_field.type}. "
                f"Valid mappings are between compatible types only."
            )


def _are_types_compatible(inferred_type: 'pa.DataType', explicit_type: 'pa.DataType') -> bool:
    """Check if explicit type is compatible with inferred type."""
    if not pa:
        return False
    
    # Use the cast compatibility from arrow_utils
    return can_cast_type(inferred_type, explicit_type)


def validate_record_batch_schema(
    record_batch: 'pa.RecordBatch', 
    expected_schema: 'pa.Schema'
) -> None:
    """
    Validate that a RecordBatch schema matches the expected schema.
    
    Args:
        record_batch: The RecordBatch to validate
        expected_schema: The expected schema
        
    Raises:
        ValidationError: If schemas don't match
    """
    if not pa:
        raise ValidationError("PyArrow is required but not installed")
    
    actual_schema = record_batch.schema
    
    # Check field count
    if len(actual_schema) != len(expected_schema):
        raise ValidationError(
            f"Schema field count mismatch: expected {len(expected_schema)}, "
            f"got {len(actual_schema)}"
        )
    
    # Create field mappings by name for alignment
    actual_fields = {field.name: field for field in actual_schema}
    expected_fields = {field.name: field for field in expected_schema}
    
    # Check field names
    actual_names = set(actual_fields.keys())
    expected_names = set(expected_fields.keys())
    
    if actual_names != expected_names:
        missing = expected_names - actual_names
        extra = actual_names - expected_names
        
        error_parts = []
        if missing:
            error_parts.append(f"missing fields {sorted(missing)}")
        if extra:
            error_parts.append(f"unexpected fields {sorted(extra)}")
        
        raise ValidationError(
            f"Schema field mismatch: {', '.join(error_parts)}. "
            f"Expected: {sorted(expected_names)}, Got: {sorted(actual_names)}"
        )
    
    # Check field types and nullability
    for field_name in expected_fields:
        expected_field = expected_fields[field_name]
        actual_field = actual_fields[field_name]
        
        if not expected_field.equals(actual_field):
            raise ValidationError(
                f"Field '{field_name}' type mismatch: "
                f"expected {expected_field.type} (nullable={expected_field.nullable}), "
                f"got {actual_field.type} (nullable={actual_field.nullable})"
            )


def get_field_alignment_mapping(
    record_batch_schema: 'pa.Schema', 
    expected_schema: 'pa.Schema'
) -> list[int]:
    """
    Get field index mapping to align RecordBatch fields with expected schema.
    
    Args:
        record_batch_schema: The actual RecordBatch schema
        expected_schema: The expected schema with desired field order
        
    Returns:
        List of indices mapping expected schema positions to RecordBatch positions
        
    Raises:
        ValidationError: If schemas are incompatible
    """
    if not pa:
        raise ValidationError("PyArrow is required but not installed")
    
    # First validate schemas are compatible by creating empty arrays for each field
    empty_arrays = [pa.array([], type=field.type) for field in record_batch_schema]
    empty_batch = pa.record_batch(empty_arrays, record_batch_schema)
    validate_record_batch_schema(empty_batch, expected_schema)
    
    # Create field name to index mapping for RecordBatch
    rb_field_indices = {field.name: i for i, field in enumerate(record_batch_schema)}
    
    # Build alignment mapping
    alignment = []
    for expected_field in expected_schema:
        rb_index = rb_field_indices[expected_field.name]
        alignment.append(rb_index)
    
    return alignment