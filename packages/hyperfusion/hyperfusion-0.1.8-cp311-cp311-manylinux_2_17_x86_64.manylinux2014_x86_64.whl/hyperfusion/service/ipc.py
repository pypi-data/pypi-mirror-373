import pyarrow as pa
import pyarrow.ipc as ipc
from typing import Optional


def serialize_record_batch(batch: pa.RecordBatch) -> bytes:
    """Serialize RecordBatch to Arrow IPC format bytes."""
    sink = pa.BufferOutputStream()
    with ipc.new_stream(sink, batch.schema) as writer:
        writer.write_batch(batch)
    return sink.getvalue().to_pybytes()


def deserialize_record_batch(data: bytes) -> pa.RecordBatch:
    """Deserialize RecordBatch from Arrow IPC format bytes."""
    buffer = pa.py_buffer(data)
    with ipc.open_stream(buffer) as reader:
        return reader.read_next_batch()


def serialize_schema(schema: pa.Schema) -> bytes:
    """Serialize schema using empty RecordBatch."""
    # Create empty arrays for each field in the schema
    arrays = []
    for field in schema:
        empty_array = pa.array([], type=field.type)
        arrays.append(empty_array)
    
    batch = pa.record_batch(arrays, schema=schema)
    return serialize_record_batch(batch)


def deserialize_schema(data: bytes) -> pa.Schema:
    """Deserialize schema from Arrow IPC format."""
    batch = deserialize_record_batch(data)
    return batch.schema


def table_to_record_batch(table: pa.Table) -> pa.RecordBatch:
    """Convert Table to RecordBatch by combining all batches."""
    if table.num_rows == 0:
        return pa.record_batch([], schema=table.schema)
    batches = table.to_batches()
    return batches[0] if len(batches) == 1 else table.combine_chunks().to_batches()[0]


def record_batch_to_table(batch: pa.RecordBatch) -> pa.Table:
    """Convert RecordBatch to Table."""
    return pa.Table.from_batches([batch])