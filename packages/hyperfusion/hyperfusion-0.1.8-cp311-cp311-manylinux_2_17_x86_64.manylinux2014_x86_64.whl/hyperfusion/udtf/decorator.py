"""Main UDTF decorator implementation."""

import inspect
from dataclasses import dataclass
from typing import Callable, Optional, Union, get_type_hints
from functools import wraps

try:
    import pyarrow as pa
except ImportError:
    pa = None

try:
    import polars as pl
except ImportError:
    pl = None

from .schema.inference import infer_input_schema, infer_output_schema
from .schema.validation import validate_schema_compatibility
from .processing.mode_detection import determine_processing_mode, ProcessingMode
from .processing.executor import execute_udtf
from .error_handling.exceptions import UDTFError, SchemaError


@dataclass
class UDTFFunction:
    """Wrapper class for UDTF-decorated functions."""
    func: Callable
    name: str = None
    explicit_input_schema: Optional[Union[pa.Schema, 'pl.Schema']] = None
    explicit_output_schema: Optional[Union[pa.Schema, 'pl.Schema']] = None
    explicit_error_schema: Optional[Union[pa.Schema, 'pl.Schema']] = None
    signature: inspect.Signature = None
    type_hints: dict = None
    input_schema: pa.Schema = None
    output_schema: pa.Schema = None
    error_schema: Optional[pa.Schema] = None
    processing_mode: ProcessingMode = None
    
    def __init__(
        self, 
        func: Callable,
        input_schema: Optional[Union[pa.Schema, 'pl.Schema']] = None,
        output_schema: Optional[Union[pa.Schema, 'pl.Schema']] = None,
        error_schema: Optional[Union[pa.Schema, 'pl.Schema']] = None
    ):
        self.func = func
        self.name = func.__name__
        self.explicit_input_schema = input_schema
        self.explicit_output_schema = output_schema
        self.explicit_error_schema = error_schema
        
        # Get function signature and type hints
        self.signature = inspect.signature(func)
        try:
            self.type_hints = get_type_hints(func)
        except (NameError, AttributeError) as e:
            raise UDTFError(f"Could not resolve type hints for function {func.__name__}: {e}")
        
        # Validate function signature
        self._validate_function_signature()
        
        # Infer schemas
        self.input_schema = self._resolve_input_schema()
        self.output_schema, self.error_schema = self._resolve_output_schemas()
        
        # Determine processing mode
        return_type = self.type_hints.get('return')
        self.processing_mode = determine_processing_mode(self.type_hints, self.signature, return_type)
        
        # Register in global registry
        self._register_in_registry()
    
        
    def _validate_function_signature(self):
        """Validate function signature meets UDTF requirements."""
        # Check function is async
        if not inspect.iscoroutinefunction(self.func):
            raise UDTFError(f"UDTF functions must be async. Function '{self.func.__name__}' is not an async function.")
        
        # Check all parameters have type hints
        for param_name, param in self.signature.parameters.items():
            if param_name not in self.type_hints:
                raise UDTFError(f"Parameter '{param_name}' missing type hint")
        
        # Check return type hint exists
        if 'return' not in self.type_hints:
            raise UDTFError(f"Function '{self.func.__name__}' missing return type hint")
        
        # Validate DataFrame parameter constraints
        self._validate_dataframe_constraints()
    
    def _validate_dataframe_constraints(self):
        """Validate DataFrame parameter constraints."""
        from .utils.type_utils import is_dataframe_type
        
        dataframe_params = []
        for param_name, param_type in self.type_hints.items():
            if param_name != 'return' and is_dataframe_type(param_type):
                dataframe_params.append(param_name)
        
        # Check DataFrame parameters are not combined with others
        if dataframe_params and len(self.signature.parameters) > 1:
            other_params = [p for p in self.signature.parameters if p not in dataframe_params]
            if other_params:
                raise UDTFError(
                    f"DataFrame parameters cannot be combined with other parameters. "
                    f"Found DataFrame parameter '{dataframe_params[0]}' along with parameter '{other_params[0]}'"
                )
        
        # Check DataFrame parameters have explicit input schema
        if dataframe_params and not self.explicit_input_schema:
            raise UDTFError(
                f"DataFrame parameter '{dataframe_params[0]}' requires explicit input schema in decorator"
            )
    
    def _resolve_input_schema(self) -> pa.Schema:
        """Resolve input schema from explicit or inferred."""
        if self.explicit_input_schema:
            # Convert polars schema to pyarrow if needed
            if pl and isinstance(self.explicit_input_schema, pl.Schema):
                self.explicit_input_schema = self.explicit_input_schema.to_arrow()
            
            inferred_schema = infer_input_schema(self.type_hints, self.signature)
            validate_schema_compatibility(self.explicit_input_schema, inferred_schema, "input")
            return self.explicit_input_schema
        else:
            return infer_input_schema(self.type_hints, self.signature)
    
    def _resolve_output_schemas(self) -> tuple[pa.Schema, Optional[pa.Schema]]:
        """Resolve output and error schemas from explicit or inferred."""
        return_type = self.type_hints['return']
        
        # Handle explicit output schema first
        output_schema = None
        if self.explicit_output_schema:
            if pl and isinstance(self.explicit_output_schema, pl.Schema):
                self.explicit_output_schema = self.explicit_output_schema.to_arrow()
            output_schema = self.explicit_output_schema
        
        # Handle explicit error schema first  
        error_schema = None
        if self.explicit_error_schema:
            if pl and isinstance(self.explicit_error_schema, pl.Schema):
                self.explicit_error_schema = self.explicit_error_schema.to_arrow()
            error_schema = self.explicit_error_schema
        
        # Only infer schemas if not explicitly provided
        if output_schema is None or error_schema is None:
            try:
                inferred_output, inferred_error = infer_output_schema(return_type, self.input_schema)
                
                if output_schema is None:
                    output_schema = inferred_output
                else:
                    # Validate compatibility if we have both explicit and inferred
                    if inferred_output:
                        validate_schema_compatibility(output_schema, inferred_output, "output")
                
                if error_schema is None:
                    error_schema = inferred_error
                else:
                    # Validate compatibility if we have both explicit and inferred
                    if inferred_error:
                        validate_schema_compatibility(error_schema, inferred_error, "error")
            
            except SchemaError as e:
                # If inference fails but we have explicit schemas, that's fine
                if output_schema is None:
                    raise e  # Re-raise if we actually need the inferred output schema
                # For error schema, create a default if inference fails
                if error_schema is None:
                    from .error_handling.error_schemas import create_default_error_schema
                    error_schema = create_default_error_schema(self.input_schema)
        
        return output_schema, error_schema
    
    def _register_in_registry(self):
        """Register this UDTF function in the global registry."""
        from .registry import registry
        registry.register(self)
    
    def __call__(self, record_batch: pa.RecordBatch) -> tuple[pa.RecordBatch, Optional[pa.RecordBatch]]:
        """Execute the UDTF function on a RecordBatch synchronously (backward compatibility)."""
        import asyncio
        try:
            # Try to get the current event loop
            loop = asyncio.get_running_loop()
            # If we're in an event loop, we can't use asyncio.run()
            raise RuntimeError("Cannot call sync method from within an async context. Use execute_async() instead.")
        except RuntimeError as e:
            if "no running event loop" in str(e).lower():
                # No event loop running, safe to use asyncio.run()
                return asyncio.run(self.execute_async(record_batch))
            else:
                # We're in an event loop, re-raise the error
                raise e
    
    async def execute_async(self, record_batch: pa.RecordBatch) -> tuple[pa.RecordBatch, Optional[pa.RecordBatch]]:
        """Execute the UDTF function on a RecordBatch asynchronously."""
        return await execute_udtf(self, record_batch)


def udtf(
    input_schema: Optional[Union[pa.Schema, 'pl.Schema']] = None,
    output_schema: Optional[Union[pa.Schema, 'pl.Schema']] = None, 
    error_schema: Optional[Union[pa.Schema, 'pl.Schema']] = None
) -> Callable:
    """
    Decorator to mark functions as User-Defined Table Functions (UDTFs).
    
    Args:
        input_schema: Explicit input schema (overrides type hint inference)
        output_schema: Explicit output schema (overrides type hint inference)
        error_schema: Explicit error schema (overrides default error handling)
    
    Returns:
        Decorated function that can process Arrow RecordBatches
    """
    # Handle both @udtf() and @udtf cases
    if callable(input_schema):
        # @udtf (no parentheses)
        func = input_schema
        return UDTFFunction(func)
    
    # @udtf(...) (with parameters)
    def decorator(func: Callable) -> UDTFFunction:
        return UDTFFunction(func, input_schema, output_schema, error_schema)
    
    return decorator