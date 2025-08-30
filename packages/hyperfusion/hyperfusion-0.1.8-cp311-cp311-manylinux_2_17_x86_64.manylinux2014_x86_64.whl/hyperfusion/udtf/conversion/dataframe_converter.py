"""DataFrame conversion utilities."""

from typing import Any, Type

try:
    import pyarrow as pa
except ImportError:
    pa = None

try:
    import pandas as pd
except ImportError:
    pd = None

try:
    import polars as pl
except ImportError:
    pl = None

from ..error_handling.exceptions import ConversionError


class DataFrameConverter:
    """Converter for DataFrame types (pandas, polars, pyarrow)."""
    
    def to_dataframe(self, record_batch: 'pa.RecordBatch', target_type: Type) -> Any:
        """
        Convert RecordBatch to target DataFrame type.
        
        Args:
            record_batch: Input RecordBatch
            target_type: Target DataFrame type (pandas.DataFrame, polars.DataFrame, pyarrow.Table)
            
        Returns:
            DataFrame of the target type
            
        Raises:
            ConversionError: If conversion fails
        """
        if not pa:
            raise ConversionError("PyArrow is required but not installed")
        
        if pd and target_type is pd.DataFrame:
            return self._to_pandas(record_batch)
        elif pl and target_type is pl.DataFrame:
            return self._to_polars(record_batch)
        elif pa and target_type is pa.Table:
            return self._to_arrow_table(record_batch)
        else:
            raise ConversionError(f"Unsupported DataFrame type: {target_type}")
    
    def from_dataframe(self, dataframe: Any, expected_schema: 'pa.Schema') -> 'pa.RecordBatch':
        """
        Convert DataFrame to RecordBatch.
        
        Args:
            dataframe: Input DataFrame
            expected_schema: Expected output schema
            
        Returns:
            RecordBatch with expected schema
            
        Raises:
            ConversionError: If conversion fails
        """
        if not pa:
            raise ConversionError("PyArrow is required but not installed")
        
        if pd and isinstance(dataframe, pd.DataFrame):
            return self._from_pandas(dataframe, expected_schema)
        elif pl and isinstance(dataframe, pl.DataFrame):
            return self._from_polars(dataframe, expected_schema)
        elif pa and isinstance(dataframe, pa.Table):
            return self._from_arrow_table(dataframe, expected_schema)
        else:
            raise ConversionError(f"Unsupported DataFrame type: {type(dataframe)}")
    
    def _to_pandas(self, record_batch: 'pa.RecordBatch') -> 'pd.DataFrame':
        """Convert RecordBatch to pandas DataFrame."""
        if not pd:
            raise ConversionError("pandas is required but not installed")
        
        try:
            return record_batch.to_pandas()
        except Exception as e:
            raise ConversionError(f"Failed to convert to pandas DataFrame: {e}")
    
    def _to_polars(self, record_batch: 'pa.RecordBatch') -> 'pl.DataFrame':
        """Convert RecordBatch to polars DataFrame."""
        if not pl:
            raise ConversionError("polars is required but not installed")
        
        try:
            # Convert via Arrow Table
            table = pa.Table.from_batches([record_batch])
            return pl.from_arrow(table)
        except Exception as e:
            raise ConversionError(f"Failed to convert to polars DataFrame: {e}")
    
    def _to_arrow_table(self, record_batch: 'pa.RecordBatch') -> 'pa.Table':
        """Convert RecordBatch to Arrow Table."""
        try:
            return pa.Table.from_batches([record_batch])
        except Exception as e:
            raise ConversionError(f"Failed to convert to Arrow Table: {e}")
    
    def _from_pandas(self, dataframe: 'pd.DataFrame', expected_schema: 'pa.Schema') -> 'pa.RecordBatch':
        """Convert pandas DataFrame to RecordBatch."""
        if not pd:
            raise ConversionError("pandas is required but not installed")
        
        try:
            # Convert to Arrow Table first
            table = pa.Table.from_pandas(dataframe, schema=expected_schema)
            # Convert to RecordBatch
            if table.num_rows > 0:
                # Ensure all data is in a single batch
                table = table.combine_chunks()
                return table.to_batches(max_chunksize=None)[0]
            else:
                # Create empty arrays for each field in the schema
                empty_arrays = []
                for field in expected_schema:
                    empty_arrays.append(pa.array([], type=field.type))
                return pa.record_batch(empty_arrays, expected_schema)
        except Exception as e:
            raise ConversionError(f"Failed to convert from pandas DataFrame: {e}")
    
    def _from_polars(self, dataframe: 'pl.DataFrame', expected_schema: 'pa.Schema') -> 'pa.RecordBatch':
        """Convert polars DataFrame to RecordBatch."""
        if not pl:
            raise ConversionError("polars is required but not installed")
        
        try:
            # Convert to Arrow Table
            table = dataframe.to_arrow()
            # Ensure schema matches
            if not table.schema.equals(expected_schema):
                table = table.cast(expected_schema)
            # Convert to RecordBatch
            if table.num_rows > 0:
                # Ensure all data is in a single batch
                table = table.combine_chunks()
                return table.to_batches(max_chunksize=None)[0]
            else:
                # Create empty arrays for each field in the schema
                empty_arrays = []
                for field in expected_schema:
                    empty_arrays.append(pa.array([], type=field.type))
                return pa.record_batch(empty_arrays, expected_schema)
        except Exception as e:
            raise ConversionError(f"Failed to convert from polars DataFrame: {e}")
    
    def _from_arrow_table(self, table: 'pa.Table', expected_schema: 'pa.Schema') -> 'pa.RecordBatch':
        """Convert Arrow Table to RecordBatch."""
        try:
            # Ensure schema matches
            if not table.schema.equals(expected_schema):
                table = table.cast(expected_schema)
            # Convert to RecordBatch
            return table.to_batches()[0] if table.num_rows > 0 else pa.record_batch([], expected_schema)
        except Exception as e:
            raise ConversionError(f"Failed to convert from Arrow Table: {e}")