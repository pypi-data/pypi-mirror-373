import grpc
from concurrent import futures
import asyncio
from typing import AsyncIterator, Optional
import pyarrow as pa
from . import hyperfusion_pb2
from . import hyperfusion_pb2_grpc
from .ipc import serialize_record_batch, deserialize_record_batch, serialize_schema, table_to_record_batch, record_batch_to_table
import logging
from asyncio import Queue
from .bus import Bus
from .messages import ExecuteFunctionRequest
from ..udtf.registry import registry

logger = logging.getLogger(__name__)


class ExecutorService(hyperfusion_pb2_grpc.ExecutionServiceServicer):
    def __init__(self, bus: Bus):
        self.bus = bus
        self.registry = registry
        self.logger = logger
        self.outgoing_queue: Optional[Queue] = None
        
    async def send_message(self, message: hyperfusion_pb2.ExecutorMessage):
        """Send a message to the connected Caller"""
        if self.outgoing_queue:
            await self.outgoing_queue.put(message)
        else:
            self.logger.warning(f"No outgoing queue available to send message")
    
    async def send_log(self, level: str, message: str):
        """Send a log message to the Caller"""
        await self.send_message(
            hyperfusion_pb2.ExecutorMessage(
                log=hyperfusion_pb2.LogMessage(
                    level=level,
                    message=message,
                    timestamp=int(asyncio.get_event_loop().time() * 1000)
                )
            )
        )
    
    async def send_executed_function(self, name: str, batch_id: str, 
                                    output_batch: Optional[bytes] = None,
                                    error_batch: Optional[bytes] = None,
                                    error: Optional[str] = None):
        """Send function execution result to the Caller"""
        msg = hyperfusion_pb2.ExecutedFunctionMessage(
            name=name,
            batch_id=batch_id,  # Use batch_id field name per protobuf definition
        )
        if output_batch:
            msg.output_record_batch = output_batch
        if error_batch:
            msg.error_record_batch = error_batch
        if error:
            msg.error = error
            
        await self.send_message(
            hyperfusion_pb2.ExecutorMessage(executed_function=msg)
        )
        
    async def Stream(self, 
                     request_iterator: AsyncIterator[hyperfusion_pb2.CallerMessage],
                     context: grpc.aio.ServicerContext
                     ) -> AsyncIterator[hyperfusion_pb2.ExecutorMessage]:
        # Create queue for outgoing messages
        self.outgoing_queue = Queue()
        
        # Send all function definitions immediately when Caller connects
        functions = []
        for name, info in self.registry.functions.items():
            functions.append(hyperfusion_pb2.FunctionDefinition(
                name=name,
                in_schema=serialize_schema(info.input_schema),
                out_schema=serialize_schema(info.output_schema),
                err_schema=serialize_schema(info.error_schema),
            ))

        # Send all functions at once
        await self.outgoing_queue.put(
            hyperfusion_pb2.ExecutorMessage(
                expose_functions=hyperfusion_pb2.ExposeFunctionsMessage(
                    functions=functions
                )
            )
        )
        
        # Create tasks for handling incoming and outgoing messages
        async def handle_incoming():
            message_count = 0
            stream_start_time = asyncio.get_event_loop().time()
            
            try:
                async for caller_msg in request_iterator:
                    message_count += 1

                    msg_type = caller_msg.WhichOneof('message')
                    
                    if msg_type is None:
                        continue
                        
                    if caller_msg.HasField('get_functions'):
                        # Re-send function definitions if requested
                        await self.outgoing_queue.put(
                            hyperfusion_pb2.ExecutorMessage(
                                expose_functions=hyperfusion_pb2.ExposeFunctionsMessage(
                                    functions=functions
                                )
                            )
                        )
                        
                    elif caller_msg.HasField('execute_function'):
                        # Publish execution request to bus for MainService to handle
                        exec_msg = caller_msg.execute_function
                        # Validate execute_function message
                        if not exec_msg.name:
                            self.logger.error(f"Invalid execute_function #{message_count}: empty function name")
                        if not exec_msg.batch_id:
                            self.logger.error(f"Invalid execute_function #{message_count}: empty batch_id")
                        if not exec_msg.input_record_batch:
                            self.logger.warning(f"execute_function #{message_count}: empty input_record_batch")
                            
                        try:
                            await self.bus.publish(ExecuteFunctionRequest(exec_msg=exec_msg))
                        except Exception as e:
                            self.logger.error(f"Failed to publish ExecuteFunctionRequest for batch_id {exec_msg.batch_id}: {e}")
                            self.logger.exception(f"Full exception details:")
                    else:
                        self.logger.warning(f"Received unknown message type: {msg_type}")
                    
            except Exception as e:
                self.logger.error(f"[Error in handle_incoming loop after {message_count} messages: {e}")
                self.logger.exception(f"[Full exception details:")
            finally:
                final_time = asyncio.get_event_loop().time() - stream_start_time
                self.logger.info(f"handle_incoming loop ended after processing {message_count} messages in {final_time:.3f}s")
        
        # Run both tasks concurrently
        incoming_task = asyncio.create_task(handle_incoming())
        
        try:
            while True:
                message = await self.outgoing_queue.get()
                if message is None:  # Sentinel to stop
                    break
                
                yield message
        except Exception as e:
            self.logger.error(f"Error in Stream handler: {e}")
            self.logger.exception(f"Full exception details:")
            raise
        finally:
            incoming_task.cancel()
            self.outgoing_queue = None
    
    async def HealthCheck(self, request, context):
        return hyperfusion_pb2.HealthStatus(ready=True, message="Healthy")


