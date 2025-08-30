import asyncio
import signal
import logging
from typing import Coroutine, List, Callable, Awaitable


class GracefulRunner:
    def __init__(self, logger: logging.Logger, on_shutdown: List[Callable[[], Awaitable[None]]] = None):
        self.logger = logger
        self.coroutines: List[Coroutine] = []
        self.running_tasks: List[asyncio.Task] = []
        self.on_shutdown_callbacks = on_shutdown if on_shutdown else []
        self.shutdown_event = asyncio.Event()

    def add(self, coro: Coroutine):
        self.coroutines.append(coro)

    async def _handle_signal(self, sig: signal.Signals):
        self.logger.info(f"Received exit signal {sig.name}. Initiating shutdown...")
        self.shutdown_event.set()

    async def run(self):
        loop = asyncio.get_event_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, lambda s=sig: asyncio.create_task(self._handle_signal(s)))

        try:
            if not self.coroutines:
                self.logger.warning("No coroutines were added. Exiting.")
                return

            self.logger.info(f"Starting {len(self.coroutines)} coroutines...")
            for coro in self.coroutines:
                self.running_tasks.append(asyncio.create_task(coro))

            self.logger.info("All coroutines are running. Press Ctrl+C to exit.")

            shutdown_waiter = asyncio.create_task(self.shutdown_event.wait())

            done, pending = await asyncio.wait(
                self.running_tasks + [shutdown_waiter],
                return_when=asyncio.FIRST_COMPLETED
            )

            if shutdown_waiter in done:
                self.logger.info("Shutdown signal received. Terminating coroutines.")
            else:
                self.logger.warning("A coroutine finished unexpectedly. Initiating shutdown.")

            for task in pending:
                task.cancel()

            await asyncio.gather(*pending, return_exceptions=True)

        finally:
            self.logger.info("Executing shutdown callbacks...")
            for callback in self.on_shutdown_callbacks:
                await callback()
            self.logger.info("Shutdown complete.")

