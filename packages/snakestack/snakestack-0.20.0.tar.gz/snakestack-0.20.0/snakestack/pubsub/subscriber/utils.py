import asyncio
import gzip
import logging
import time
from concurrent.futures import Future as CFuture
from typing import Any, Optional, Sequence, Type

import orjson

try:
    from google.cloud.pubsub_v1 import SubscriberClient
    from google.cloud.pubsub_v1.subscriber.message import Message
except ImportError:
    raise RuntimeError("Pubsub extra is not installed. Run `pip install snakestack[pubsub]`.")

from pydantic import BaseModel, ValidationError

from .exceptions import AckableError

logger = logging.getLogger(__name__)


def parse_message(message: Message, schema: Type[BaseModel] | None = None) -> Any:
    raw_bytes = message.data
    encoding = message.attributes.get("encoding", "").lower()
    if encoding == "gzip":
        try:
            raw_data = gzip.decompress(raw_bytes).decode("utf-8")
        except Exception as e:
            raise AckableError(f"Error on decompress: {e}")
    else:
        raw_data = raw_bytes.decode("utf-8")

    try:
        parsed_data = orjson.loads(raw_data)
    except orjson.JSONDecodeError:
       return {"data": raw_data, "valid_json": False}

    if schema:
        try:
            parsed_data = schema(**parsed_data)
        except ValidationError as e:
            raise AckableError(f"Validation error: {e}")

    return {"valid_json": True, "data": parsed_data}


def get_message_info(message: Message) -> tuple[float, float]:
    publish_time = message.publish_time.timestamp()
    latency_ms = (time.time() - publish_time) * 1000
    message_kb = message.size / 1024
    return latency_ms, message_kb


async def ack_messages(
    messages: Sequence[Message],
    *,
    subscriber_client: Optional[SubscriberClient] = None,
    subscription_path: Optional[str] = None,
    batch_threshold: int = 100,
) -> None:
    if not messages:
        return

    if not subscriber_client or not subscription_path or len(messages) < batch_threshold:
        logger.debug(f"Ack [{len(messages)}] messages")
        for msg in messages:
            msg.ack()
        return

    ack_ids = [msg.ack_id for msg in messages]
    logger.debug(f"Ack in batch [{len(ack_ids)}] messages")
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(
        None,
        subscriber_client.acknowledge,
        subscription_path,
        ack_ids,
    )


async def nack_messages(
    messages: Sequence[Message],
) -> None:
    if not messages:
        return

    for msg in messages:
        msg.nack()


def future_callback(future: CFuture[None]) -> None:
    if future.cancelled():
        logger.warning("Enqueue cancelled")
        return
    exc = future.exception()
    if exc:
        logger.error(
            "Enqueue error",
            exc_info=(type(exc), exc, exc.__traceback__),
        )
