import asyncio
import logging
import time
from typing import Awaitable, Callable, Self, TypeAlias

try:
    from google.cloud.pubsub_v1 import SubscriberClient
    from google.cloud.pubsub_v1.subscriber.message import Message
except ImportError:
    raise RuntimeError("Pubsub extra is not installed. Run `pip install snakestack[pubsub]`.")

from snakestack.model import LenientModel
from snakestack.pubsub.subscriber.types import AsyncQueueMessagePubSub, DataPubSubType

logger = logging.getLogger(__name__)


class BatchSettingsModel(LenientModel):
    size: int
    timeout: float
    name: str
    subscriber_client: SubscriberClient | None = None
    subscription_path: str | None = None


class BatchingWorker:
    def __init__(
        self: Self,
        *,
        callback: Callable[[list[tuple[Message, DataPubSubType]], BatchSettingsModel], Awaitable[None]],
        batch_settings: BatchSettingsModel
    ) -> None:
        self.buffer: list[tuple[Message, DataPubSubType]] = []
        self.last_flush = time.monotonic()
        self.callback = callback
        self.batch_settings = batch_settings
        self._queue: AsyncQueueMessagePubSub | None = None

    async def run(
        self: Self,
        queue: AsyncQueueMessagePubSub
    ) -> None:
        self._queue = queue
        try:
            logger.debug(f"Starting batch [{self.batch_settings.name}] "
                         f"- Timeout [{self.batch_settings.timeout}] "
                         f"- Size [{self.batch_settings.size}]")
            while True:
                try:
                    timeout = self._get_timeout()
                    item = await asyncio.wait_for(queue.get(), timeout=timeout)
                    self.buffer.append(item)
                except asyncio.TimeoutError:
                    pass

                conditional_size = self._get_size_conditional()
                conditional_time = self._get_time_conditional()
                if any([conditional_time, conditional_size]):
                    await self._flush()
        except asyncio.CancelledError:
            await self._flush()
            raise

    async def _flush(self: Self) -> None:
        if not self.buffer:
            return

        logger.info(f"[{self.batch_settings.name}] Executing batch with {len(self.buffer)} messages")
        try:
            await self.callback(self.buffer, self.batch_settings)
        except Exception:
            logger.exception("Failed to process batch")
        finally:
            if self._queue:
                for _ in range(len(self.buffer)):
                    self._queue.task_done()
            self.buffer.clear()
            self.last_flush = time.monotonic()

    def _get_size_conditional(self: Self) -> bool:
        return len(self.buffer) >= self.batch_settings.size

    def _get_time_conditional(self: Self) -> bool:
        return (time.monotonic() - self.last_flush) >= self.batch_settings.timeout

    def _get_timeout(self: Self) -> float:
        return max(
            self.batch_settings.timeout - (time.monotonic() - self.last_flush), 0.1
        )

BatchesType: TypeAlias = dict[str, BatchingWorker]
