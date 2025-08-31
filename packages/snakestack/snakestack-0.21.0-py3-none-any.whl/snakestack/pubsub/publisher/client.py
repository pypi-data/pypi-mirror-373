import logging
from concurrent.futures import Future
from typing import Callable, Self

try:
    from google.cloud.pubsub_v1 import PublisherClient
except ImportError:
    raise RuntimeError("Pubsub extra is not installed. Run `pip install snakestack[pubsub]`.")

from snakestack.pubsub.exceptions import InvalidAttributesError, PublishError

logger = logging.getLogger(__name__)


class SnakeStackPublisher:

    def __init__(self: Self, client: "PublisherClient") -> None:
        self.client = client

    def publish(
        self: Self,
        project_id: str,
        topic_name: str,
        data: bytes,
        attributes: dict[str, str | bytes] | None = None,
        callback: Callable[[Future[None]], None] | None = None,
        timeout: int = 5
    ) -> None:
        topic_path = self.client.topic_path(project=project_id, topic=topic_name)
        attributes = attributes or {}

        for k, v in attributes.items():
            if not isinstance(v, (str, bytes)):
                raise InvalidAttributesError(key=k, value=v)

        future = self.client.publish(data=data, topic=topic_path, **attributes)

        if callback:
            future.add_done_callback(callback)
            logger.debug(f"Callback added to future for topic {topic_path}")
        else:
            try:
                future.result(timeout=timeout)
            except Exception as e:
                logger.exception("Error while publishing message.", exc_info=e)
                raise PublishError(topic=topic_path, original_exception=e)
            else:
                logger.debug(f"Successfully sent on topic {topic_path}")
