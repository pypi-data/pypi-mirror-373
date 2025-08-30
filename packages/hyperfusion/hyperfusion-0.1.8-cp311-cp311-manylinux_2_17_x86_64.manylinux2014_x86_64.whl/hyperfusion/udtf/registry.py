"""Registry system for Arrow UDTF functions."""

from typing import Dict, List, Optional, Tuple
import pyarrow as pa
from .decorator import UDTFFunction


class UDTFRegistry:
    """Registry to track all decorated UDTF functions."""
    
    def __init__(self):
        self._functions: Dict[str, UDTFFunction] = {}
    
    def register(self, udtf_function: UDTFFunction) -> None:
        """
        Register a UDTF function in the registry.
        
        Args:
            udtf_function: The UDTFFunction instance to register
            
        Raises:
            ValueError: If a function with the same name is already registered
        """
        name = udtf_function.func.__name__
        
        if name in self._functions:
            raise ValueError(f"UDTF with name '{name}' is already registered")
        
        self._functions[name] = udtf_function
    
    def get(self, name: str) -> UDTFFunction:
        """
        Get a registered UDTF function by name.
        
        Args:
            name: The name of the UDTF function
            
        Returns:
            The UDTFFunction instance
            
        Raises:
            KeyError: If no function with the given name is registered
        """
        if name not in self._functions:
            raise KeyError(f"UDTF '{name}' not found")
        
        return self._functions[name]
    
    def list(self) -> List[UDTFFunction]:
        """
        Get a list of all registered UDTF functions.
        
        Returns:
            List of all registered UDTFFunction instances
        """
        return list(self._functions.values())
    
    def names(self) -> List[str]:
        """
        Get a list of all registered UDTF function names.
        
        Returns:
            List of function names
        """
        return list(self._functions.keys())
    
    def clear(self) -> None:
        """Clear all registered functions."""
        self._functions.clear()
    
    def unregister(self, name: str) -> Optional[UDTFFunction]:
        """
        Unregister a UDTF function by name.
        
        Args:
            name: The name of the UDTF function to unregister
            
        Returns:
            The unregistered UDTFFunction instance, or None if not found
        """
        return self._functions.pop(name, None)
    
    def __len__(self) -> int:
        """Return the number of registered functions."""
        return len(self._functions)
    
    def __contains__(self, name: str) -> bool:
        """Check if a function name is registered."""
        return name in self._functions
    
    async def execute(self, name: str, input_table: pa.Table) -> Tuple[Optional[pa.Table], Optional[pa.Table]]:
        """
        Execute a registered UDTF function.
        
        Args:
            name: The name of the UDTF function to execute
            input_table: The input data as an Arrow Table
            
        Returns:
            Tuple of (output_table, error_table)
            
        Raises:
            KeyError: If no function with the given name is registered
        """
        udtf_function = self.get(name)
        
        # Convert table to record batch for execution
        if input_table.num_rows == 0:
            input_batch = pa.record_batch([], schema=input_table.schema)
        else:
            batches = input_table.to_batches()
            input_batch = batches[0] if len(batches) == 1 else input_table.combine_chunks().to_batches()[0]
        
        # Execute the function
        output_batch, error_batch = await udtf_function.execute_async(input_batch)
        
        # Convert results back to tables
        output_table = pa.Table.from_batches([output_batch]) if output_batch is not None else None
        error_table = pa.Table.from_batches([error_batch]) if error_batch is not None else None
        
        return output_table, error_table

    @property
    def functions(self) -> Dict[str, UDTFFunction]:
        """Get the internal functions dictionary for gRPC integration."""
        return self._functions


# Global registry instance
registry = UDTFRegistry()