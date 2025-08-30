"""Main service that handles business logic for UDTF execution."""

import logging
from dataclasses import dataclass
import pyarrow as pa

from .bus import Bus
from ..udtf.registry import registry, UDTFRegistry
from .ipc import serialize_record_batch, deserialize_record_batch, table_to_record_batch
from .messages import ExecuteFunctionRequest, LogMessage


@dataclass
class MainService:
    """Service that handles UDTF execution and message routing."""
    
    bus: Bus
    logger: logging.Logger
    grpc_service: 'ExecutorService'
    registry: UDTFRegistry
    
    def __post_init__(self):
        """Subscribe to bus messages."""
        self.bus.subscribe(ExecuteFunctionRequest, self.handle_execute_function)
        self.bus.subscribe(LogMessage, self.handle_log_message)
    
    async def handle_log_message(self, msg: LogMessage):
        """Forward log messages to the Caller via gRPC."""
        await self.grpc_service.send_log(msg.level, msg.message)
    
    async def handle_execute_function(self, msg: ExecuteFunctionRequest):
        """Handle function execution request from gRPC."""
        exec_msg = msg.exec_msg
        
        try:
            # Get the UDTF function
            # udtf = registry.get(exec_msg.name)
            
            # Deserialize input
            input_batch = deserialize_record_batch(exec_msg.input_record_batch)  # Updated field name
            input_table = pa.Table.from_batches([input_batch])

            
            # Execute the function
            output_table, error_table = await self.registry.execute(exec_msg.name, input_table)
            
            # Serialize results
            output_batch_bytes = None
            if output_table is not None and output_table.num_rows > 0:
                output_batch = table_to_record_batch(output_table)
                output_batch_bytes = serialize_record_batch(output_batch)
            
            error_batch_bytes = None
            if error_table is not None and error_table.num_rows > 0:
                error_batch = table_to_record_batch(error_table)
                error_batch_bytes = serialize_record_batch(error_batch)
            
            # Send response via gRPC
            await self.grpc_service.send_executed_function(
                name=exec_msg.name,
                batch_id=exec_msg.batch_id,  # Updated field name
                output_batch=output_batch_bytes,
                error_batch=error_batch_bytes
            )
            
        except KeyError as e:
            error_msg = f"Function not found: {exec_msg.name}"
            await self.grpc_service.send_executed_function(
                name=exec_msg.name,
                batch_id=exec_msg.batch_id,  # Updated field name
                error=f"FUNCTION_NOT_FOUND: {error_msg}"
            )
        except Exception as e:
            error_msg = f"Error executing function {exec_msg.name}: {str(e)}"
            self.logger.exception(f"Full exception details for batch_id {exec_msg.batch_id}:")
            await self.grpc_service.send_executed_function(
                name=exec_msg.name,
                batch_id=exec_msg.batch_id,  # Updated field name
                error=f"EXECUTION_ERROR: {str(e)}"
            )