import asyncio
import signal

from .client import SnakeStackSubscriber


def setup_signal_handlers(subscriber: SnakeStackSubscriber) -> None:
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, subscriber.shutdown)
