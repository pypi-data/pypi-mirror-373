import asyncio
import logging
from dataclasses import field, dataclass
from typing import Dict, Type, Any, List, Callable, Awaitable, TypeVar

T = TypeVar('T')

@dataclass
class Bus:
    _listeners: Dict[Type[Any], List[Callable[[Any], Awaitable[None]]]] = field(default_factory=dict)

    def subscribe(self, event_type: Type[T], listener: Callable[[T], Awaitable[None]]) -> None:
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(listener)

    def unsubscribe(self, event_type: Type[T], listener: Callable[[T], Awaitable[None]]) -> None:
        if event_type in self._listeners:
            self._listeners[event_type].remove(listener)

    async def publish(self, event: T) -> None:
        event_type = type(event)
        
        if event_type in self._listeners:
            listeners = self._listeners[event_type]
            
            try:
                tasks = []
                for i, listener in enumerate(listeners):
                    tasks.append(listener(event))
                
                await asyncio.gather(*tasks)
            except Exception as e:
                logging.error(f"Error processing listeners for {event_type.__name__}: {e}")
                logging.exception(f"Full exception details:")
                raise
        else:
            logging.warning(f"No listeners found for event type: {event_type.__name__}")