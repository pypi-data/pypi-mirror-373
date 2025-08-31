import asyncio
from typing import Any, Type, TypeAlias

try:
    from google.cloud.pubsub_v1.subscriber.message import Message
except ImportError:
    raise RuntimeError("Pubsub extra is not installed. Run `pip install snakestack[pubsub]`.")

from pydantic import BaseModel

AttributesPubSubType: TypeAlias = dict[str, str]
MessagePubSubType: TypeAlias = Message
DataPubSubType: TypeAlias = dict[str, Any]
BufferPubSubType: TypeAlias = list[tuple[Message, DataPubSubType]]
AsyncQueueMessagePubSub: TypeAlias = asyncio.Queue[MessagePubSubType]
QueuesType: TypeAlias = dict[str, AsyncQueueMessagePubSub]
SchemaType: TypeAlias = Type[BaseModel]
Sentinel = object()
