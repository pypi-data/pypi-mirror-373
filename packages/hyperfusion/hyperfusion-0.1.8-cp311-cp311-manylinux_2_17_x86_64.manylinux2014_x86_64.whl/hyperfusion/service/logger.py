import logging
import time
from typing import Dict, Any
from .bus import Bus
from .messages import LogMessage


def with_fields(logger: logging.Logger, fields: Dict[str, Any]) -> logging.Logger:
    return WithFields(logger, fields)

class WithFields(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        if "extra" not in kwargs:
            kwargs["extra"] = {}
        kwargs["extra"].update(self.extra)
        return msg, kwargs


class BusHandler(logging.Handler):
    def __init__(self, bus: Bus):
        super().__init__()
        self.bus = bus

    def emit(self, record):
        try:
            # Schedule the bus publish to run in the event loop
            import asyncio
            try:
                loop = asyncio.get_running_loop()
                # Publish log message for MainService to forward via gRPC
                loop.create_task(self.bus.publish(
                    LogMessage(level=record.levelname, message=record.getMessage())
                ))
            except RuntimeError:
                # No event loop running, skip logging
                pass
        except Exception:
            self.handleError(record)


def get_logger(level: int, bus: Bus) -> logging.Logger:
    logger = logging.getLogger("busLogger")
    logger.setLevel(level)

    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()

    # Add bus handler for forwarding logs via gRPC
    bus_handler = BusHandler(bus)
    logger.addHandler(bus_handler)
    
    # Add stdout handler for local console output
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger
