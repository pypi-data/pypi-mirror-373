from abc import ABC
from typing import Protocol, Self, runtime_checkable

from snakestack.pubsub.subscriber.batch import BatchSettingsModel
from snakestack.pubsub.subscriber.types import (
    AsyncQueueMessagePubSub,
    BufferPubSubType,
    DataPubSubType,
    MessagePubSubType,
    QueuesType,
)


@runtime_checkable
class SimpleProtocol(Protocol):
    async def process(
        self: Self,
        data: DataPubSubType,
        message: MessagePubSubType
    ) -> None:
        ...

@runtime_checkable
class BatchProtocol(Protocol):

    _queues: QueuesType

    async def process(
        self: Self,
        data: DataPubSubType,
        message: MessagePubSubType
    ) -> None: ...

    async def process_batch(
        self: Self,
        items: BufferPubSubType,
        batch_settings: BatchSettingsModel
    ) -> None:
        ...

class SimpleProcessor(ABC):
    async def process(
        self: Self,
        data: DataPubSubType,
        message: MessagePubSubType
    ) -> None:
        raise NotImplementedError(
            "Missing implementation of 'process'. "
            "This method is required for Pub/Sub processing in custom subscribers."
        )

class BatchProcessor(SimpleProcessor):
    def __init__(self: Self) -> None:
        self._queues: QueuesType | None = None

    async def process_batch(
        self: Self,
        items: BufferPubSubType,
        batch_settings: BatchSettingsModel
    ) -> None:
        raise NotImplementedError(
            "Missing implementation of 'process_batch'. "
            "This method is required for batched Pub/Sub processing in custom subscribers."
        )

    def set_queues(self: Self, queues: QueuesType) -> None:
        self._queues = queues

    def get_queue(self: Self, context: str) -> AsyncQueueMessagePubSub:
        if not self._queues:
            raise AttributeError("Queue is not initialized")
        return self._queues[context]
