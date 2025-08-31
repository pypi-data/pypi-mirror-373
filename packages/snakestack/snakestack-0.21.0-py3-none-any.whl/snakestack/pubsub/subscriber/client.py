import asyncio
import logging
from asyncio.events import AbstractEventLoop
from typing import Self

try:
    from google.cloud.pubsub_v1 import SubscriberClient
    from google.cloud.pubsub_v1.subscriber.futures import StreamingPullFuture
    from google.cloud.pubsub_v1.types import FlowControl, SubscriberOptions
except ImportError:
    raise RuntimeError("Pubsub extra is not installed. Run `pip install snakestack[pubsub]`.")

from snakestack.task import SnakeTaskProcess

from .batch import BatchesType, BatchingWorker, BatchSettingsModel
from .exceptions import AckableError, RetryableError
from .processors import BatchProcessor, SimpleProcessor
from .types import (
    AsyncQueueMessagePubSub,
    MessagePubSubType,
    QueuesType,
    SchemaType,
    Sentinel,
)
from .utils import (
    ack_messages,
    future_callback,
    get_message_info,
    nack_messages,
    parse_message,
)

logger = logging.getLogger(__name__)

class SnakeStackSubscriber:

    def __init__(
        self: Self,
        client: "SubscriberClient",
        subscription_path: str,
        flow_control: FlowControl,
        processor: SimpleProcessor | BatchProcessor,
        schema: SchemaType | None = None
    ) -> None:
        self.client: "SubscriberClient" = client
        self.subscription_path: str = subscription_path
        self.processor = processor
        self._max_latency_ms: float | None = None
        self._streaming_pull_future: StreamingPullFuture | None = None
        self._flow_control: FlowControl = flow_control
        self._is_batch: bool = hasattr(processor, "process_batch")
        self._loop: AbstractEventLoop | None = None
        self._event: asyncio.Event = asyncio.Event()
        self._process: SnakeTaskProcess | None = None
        self._queue: AsyncQueueMessagePubSub | None = None
        self._schema: SchemaType | None = schema
        self._contexts: list[BatchSettingsModel] = []
        self._batches: BatchesType = {}
        self._queues: QueuesType = {}
        self._tasks: list[asyncio.Task[None]] = []
        self._batch_tasks: list[asyncio.Task[None]] = []

    @classmethod
    def from_processor(
        cls: type[Self],
        project_id: str,
        subscription_name: str,
        processor: SimpleProcessor | BatchProcessor,
        *,
        flow_control: FlowControl,
        enable_open_telemetry: bool = False,
        schema: SchemaType | None = None
    ) -> Self:
        subscriber_options = SubscriberOptions(
            enable_open_telemetry_tracing=enable_open_telemetry
        )
        client = SubscriberClient(subscriber_options=subscriber_options)
        subscription_path = client.subscription_path(project_id, subscription_name)
        return cls(
            client=client,
            subscription_path=subscription_path,
            flow_control=flow_control,
            processor=processor,
            schema=schema
        )

    @property
    def loop(self) -> AbstractEventLoop:
        if self._loop is None:
            raise RuntimeError("Loop is not defined. Call await .start() in async context.")
        return self._loop

    @property
    def process(self) -> SnakeTaskProcess:
        if self._process is None:
            raise RuntimeError("Process is not defined. Call await .start() in async context.")
        return self._process

    @property
    def queue(self) -> AsyncQueueMessagePubSub:
        if not self._queue:
            self._queue = asyncio.Queue(maxsize=self._flow_control.max_messages or 100)
        return self._queue

    async def start(
        self: Self,
        max_latency_ms: float | None = None,
        num_workers: int = 2,
        queue_max_size: int = 100,
        concurrency: int | None = 5,
        contexts: list[BatchSettingsModel] | None = None
    ) -> None:
        logger.info(f"Starting consumer with {self.subscription_path}")
        self._max_latency_ms = max_latency_ms
        self._contexts = contexts or []

        self._process = SnakeTaskProcess(
            queue_max_size=queue_max_size,
            sentinel=Sentinel,
            concurrency=concurrency,
            func_callback=self.process_message,
            num_workers=num_workers
        )
        self._loop = asyncio.get_running_loop()

        self._streaming_pull_future = self.client.subscribe(
            subscription=self.subscription_path,
            callback=self._wrapper,
            flow_control=self._flow_control
        )
        logger.info("Streaming pull started")

        await self.setup_workers()
        await self.setup_batch()

        await self._event.wait()
        await self.stop()

    async def setup_workers(self) -> None:
        for i in range(self.process.num_workers):
            logger.info(f"Scheduling worker [{i}]")
            task = asyncio.create_task(self.process.worker(num=i))
            self._tasks.append(task)

    async def setup_batch(self) -> None:
        if hasattr(self.processor, "process_batch") and hasattr(self.processor, "set_queues"):
            for context in self._contexts:
                batch = BatchingWorker(
                    batch_settings=context,
                    callback=self.processor.process_batch
                )
                queue: AsyncQueueMessagePubSub = asyncio.Queue(maxsize=context.size * 2)
                task = asyncio.create_task(batch.run(queue=queue))
                self._batch_tasks.append(task)
                self._batches[context.name] = batch
                self._queues[context.name] = queue

            self.processor.set_queues(self._queues)

    async def stop(
        self: Self
    ) -> None:
        logger.info(f"Finishing consumer with {self.subscription_path}")

        if self._streaming_pull_future and not self._streaming_pull_future.cancelled():
            self._streaming_pull_future.cancel()

        await self.process.stop()
        await self.process.wait()

        if self._queues:
            await asyncio.gather(*(q.join() for q in self._queues.values()))

        for name, batch in self._batches.items():
            await batch._flush()

        for batch_task in self._batch_tasks:
            batch_task.cancel()

        await asyncio.gather(*self._batch_tasks, return_exceptions=True)
        await asyncio.gather(*self._tasks, return_exceptions=True)

    def shutdown(
        self: Self
    ) -> None:
        logger.debug("Shutdown signal received.")
        self._event.set()

    def _wrapper(
        self: Self,
        message: MessagePubSubType
    ) -> None:
        logger.debug(f"Received raw message {message.message_id}")
        future = asyncio.run_coroutine_threadsafe(
            self.process.enqueue(message=message), self.loop
        )
        future.add_done_callback(future_callback)

    async def process_message(
        self: Self,
        num: int,
        message: MessagePubSubType
    ) -> None:
        try:
            _, _ = get_message_info(message=message)
            parsed_message = parse_message(message=message, schema=self._schema)
            await self.processor.process(data=parsed_message, message=message)
            if not self._is_batch:
                await ack_messages(messages=[message])
        except AckableError:
            logger.exception("Ackable error - Message will be discarded")
            await ack_messages(messages=[message])
        except RetryableError:
            logger.exception("Retryable error - Message will be enqueued")
            await nack_messages(messages=[message])
        except Exception:
            logger.exception("Unexpected error - Message will be discarded")
            await ack_messages(messages=[message])
