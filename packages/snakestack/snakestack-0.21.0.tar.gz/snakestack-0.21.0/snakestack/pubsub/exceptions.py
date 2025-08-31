from typing import Self


class SnakeStackPubSubError(Exception):
    """Base exception for SnakeStack PubSub errors."""


class PublishError(SnakeStackPubSubError):
    """Raised when publishing a message fails."""

    def __init__(self: Self, topic: str, original_exception: Exception) -> None:
        super().__init__(f"Failed to publish message to topic '{topic}': {original_exception}")
        self.topic = topic
        self.original_exception = original_exception


class InvalidAttributesError(SnakeStackPubSubError):
    """Raised when attributes passed to publish are invalid."""

    def __init__(self: Self, key: str, value: object) -> None:
        super().__init__(f"Attribute '{key}' must be str or bytes, got {type(value).__name__}")
        self.key = key
        self.value = value
