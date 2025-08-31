import asyncio
import logging
from typing import Any, Awaitable, Callable, Self

logger = logging.getLogger(__name__)


class SnakeTaskProcess:
    def __init__(
        self: Self,
        queue_max_size: int = 100,
        func_callback: Callable[..., Awaitable[Any]] | None = None,
        sentinel: Any = None,
        concurrency: int | None = 5,
        num_workers: int = 2
    ) -> None:
        self.queue = asyncio.Queue[Any](maxsize=queue_max_size)
        self.sentinel = sentinel
        self.func_callback = func_callback
        self.semaphore = asyncio.BoundedSemaphore(concurrency) if concurrency else None
        self.num_workers = num_workers

    async def enqueue(self: Self, message: Any) -> None:
        logger.debug(f"Queue size: {self.queue.qsize()}")
        await self.queue.put(message)

    async def wait(self: Self) -> None:
        await self.queue.join()

    async def worker(
        self: Self,
        num: int
    ) -> None:
        logger.info(f"Starting worker [{num}]")
        try:
            while True:
                logger.debug(f"Worker [{num}] waiting messages...")
                message = await self.queue.get()

                if message is self.sentinel:
                    self.queue.task_done()
                    logger.debug(f"Worker [{num}] finished after sentinel")
                    break

                try:
                    logger.debug(f"Worker [{num}] pulled message")
                    cb = self.func_callback or self.callback

                    if self.semaphore:
                        async with self.semaphore:
                            await cb(num=num, message=message)
                    else:
                        await cb(num=num, message=message)
                except Exception as _:
                    logger.exception("Error on process")
                finally:
                    self.queue.task_done()

        except asyncio.CancelledError:
            logger.debug(f"Worker [{num}] cancelled while waiting; exiting.")
            raise

    async def callback(
        self: Self,
        num: int,
        message: Any
    ) -> None:
        await asyncio.sleep(0.1)
        logger.debug(f"Worker [{num}] process item {message}")

    async def stop(
        self: Self
    ) -> None:
        logger.debug("Publishing sentinels")
        for i in range(self.num_workers):
            await self.enqueue(message=self.sentinel)
