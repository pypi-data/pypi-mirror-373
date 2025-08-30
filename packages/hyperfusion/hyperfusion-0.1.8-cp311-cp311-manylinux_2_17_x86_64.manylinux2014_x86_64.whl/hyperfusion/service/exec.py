import asyncio
import inspect
import json
from dataclasses import fields, is_dataclass
from typing import Tuple

import pyarrow

from .registry import UDTF


def _flatten_dataclass_to_dict(obj, prefix=""):
    result = {}
    for field in fields(obj):
        field_name = f"{prefix}{field.name}" if prefix else field.name
        value = getattr(obj, field.name)
        
        if isinstance(value, list):
            if value and is_dataclass(value[0]):
                result[field_name] = [_dataclass_to_dict(item) for item in value]
            else:
                result[field_name] = value
        elif is_dataclass(value):
            result.update(_flatten_dataclass_to_dict(value, f"{field_name}_"))
        else:
            result[field_name] = value
    return result


def _dataclass_to_dict(obj):
    return {f.name: getattr(obj, f.name) for f in fields(obj)}


async def execute_udtf(udtf: UDTF, table: pyarrow.Table) -> Tuple[pyarrow.Table | None, pyarrow.Table | None]:
    """Execute UDTF using Arrow UDTF system if available, fallback to legacy execution."""
    
    # Try Arrow UDTF execution first
    if udtf.arrow_executor and udtf.arrow_udtf_function:
        try:
            return await execute_udtf_with_arrow(udtf, table)
        except Exception as e:
            print(f"Arrow UDTF execution failed for {udtf.name}, falling back to legacy: {e}")
    
    # Fallback to legacy execution
    return await execute_udtf_legacy(udtf, table)


async def execute_udtf_with_arrow(udtf: UDTF, table: pyarrow.Table) -> Tuple[pyarrow.Table | None, pyarrow.Table | None]:
    """Execute UDTF using the Arrow UDTF system with async support."""
    
    # Convert table to RecordBatch for Arrow UDTF processing
    if table.num_rows == 0:
        return None, None
    
    # Convert legacy flattened table to Arrow UDTF compatible format
    record_batch = convert_legacy_table_to_arrow_udtf_format(table, udtf)
    
    # For async functions, we need to handle them specially
    # Since Arrow UDTF expects sync functions, we need to create an async-aware processor
    
    if udtf.is_async:
        # Handle async functions by executing them row by row
        # This is a bridge between Arrow UDTF's sync processing and async functions
        return await execute_async_udtf_with_arrow_bridge(udtf, record_batch)
    else:
        # Direct Arrow UDTF execution for sync functions
        success_batch, error_batch = udtf.arrow_executor.execute(record_batch)
        
        # Convert back to tables
        success_table = pyarrow.Table.from_batches([success_batch]) if success_batch else None
        error_table = pyarrow.Table.from_batches([error_batch]) if error_batch else None
        
        return success_table, error_table


def convert_legacy_table_to_arrow_udtf_format(table: pyarrow.Table, udtf: UDTF) -> pyarrow.RecordBatch:
    """Convert legacy flattened table format to Arrow UDTF compatible format."""
    
    if udtf.in_type == 'dataclass' and udtf.arrow_in_schema:
        # For dataclass parameters, we need to convert flattened fields to struct
        param_name = list(inspect.signature(udtf.func).parameters.keys())[0]
        
        # Get the struct field from Arrow UDTF schema
        struct_field = udtf.arrow_in_schema[0]
        struct_type = struct_field.type
        
        # Convert table data to struct format
        struct_arrays = []
        
        for i in range(table.num_rows):
            row_dict = {}
            for field in struct_type:
                # Get value from flattened table
                if field.name in table.column_names:
                    row_dict[field.name] = table.column(field.name)[i].as_py()
                else:
                    row_dict[field.name] = None
            struct_arrays.append(row_dict)
        
        # Create struct array
        struct_array = pyarrow.array(struct_arrays, type=struct_type)
        
        # Create RecordBatch with struct column
        return pyarrow.record_batch([struct_array], schema=udtf.arrow_in_schema)
    
    else:
        # For tuple parameters, format is already compatible
        return table.to_batches()[0] if table.num_rows > 0 else pyarrow.record_batch([], table.schema)


async def execute_async_udtf_with_arrow_bridge(udtf: UDTF, record_batch: pyarrow.RecordBatch) -> Tuple[pyarrow.Table | None, pyarrow.Table | None]:
    """Bridge between Arrow UDTF system and async function execution."""
    
    # For now, fall back to legacy execution for async functions
    # TODO: Implement proper async support in Arrow UDTF system
    table = pyarrow.Table.from_batches([record_batch])
    return await execute_udtf_legacy(udtf, table)


async def execute_udtf_legacy(udtf: UDTF, table: pyarrow.Table) -> Tuple[pyarrow.Table | None, pyarrow.Table | None]:
    """Legacy UDTF execution (original implementation)."""
    tasks = []
    for i in range(table.num_rows):
        row = table.slice(i, 1)
        if udtf.in_type == 'dataclass':
            dc_type = list(inspect.signature(udtf.func).parameters.values())[0].annotation
            kwargs = {}
            for field in fields(dc_type):
                kwargs[field.name] = row.column(field.name)[0].as_py()
            instance = dc_type(**kwargs)
            tasks.append(udtf.func(instance))
        else:
            args = [col[0].as_py() for col in row.columns]
            tasks.append(udtf.func(*args))

    results = await asyncio.gather(*tasks, return_exceptions=True)

    out_records = []
    err_records = []

    for result in results:
        if isinstance(result, Exception):
            if udtf.err_schema:
                err_record = {}
                for field in udtf.err_schema:
                    if field.name == 'exception':
                        err_record[field.name] = str(result)
                    else:
                        err_record[field.name] = None
                err_records.append(err_record)
        else:
            if isinstance(result, tuple) and len(result) == 2:
                success, error = result
                if success is not None:
                    if is_dataclass(success):
                        out_records.append(_flatten_dataclass_to_dict(success))
                    else:
                        pass
                if error is not None:
                    if is_dataclass(error):
                        err_record = _flatten_dataclass_to_dict(error)
                        err_record['exception'] = None
                        err_records.append(err_record)
                    else:
                        pass
            else:
                if isinstance(result, list):
                    for item in result:
                        if is_dataclass(item):
                            out_records.append(_flatten_dataclass_to_dict(item))
                elif is_dataclass(result):
                    out_records.append(_flatten_dataclass_to_dict(result))

    out_table = None
    if udtf.out_schema and out_records:
        out_table = pyarrow.Table.from_pylist(out_records, schema=udtf.out_schema)

    err_table = None
    if udtf.err_schema and err_records:
        err_table = pyarrow.Table.from_pylist(err_records, schema=udtf.err_schema)

    return out_table, err_table
