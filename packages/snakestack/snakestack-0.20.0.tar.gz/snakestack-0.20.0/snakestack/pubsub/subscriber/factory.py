from typing import Self

try:
    from google.cloud.pubsub_v1.types import FlowControl
except ImportError:
    raise RuntimeError("Pubsub extra is not installed. Run `pip install snakestack[pubsub]`.")

from snakestack import constants


class PubSubFlowControlFactory:

    def __init__(self: Self) -> None:
        self._presets = {
            "low_latency": self.low_latency,
            "balanced": self.balanced,
            "high_throughput": self.high_throughput,
            "aggressive": self.aggressive,
        }

    def create(
        self: Self,
        max_messages: int,
        max_bytes: int,
        max_lease_duration: int
    ) -> FlowControl:
        return FlowControl(
            max_messages=max_messages,
            max_bytes=max_bytes,
            max_lease_duration=max_lease_duration
        )

    def low_latency(self: Self) -> FlowControl:
        return self.create(
            max_messages=1,
            max_bytes=10 * constants.KILOBYTE,
            max_lease_duration=10 * constants.SECONDS
        )

    def balanced(self: Self) -> FlowControl:
        return self.create(
            max_messages=10,
            max_bytes=100 * constants.KILOBYTE,
            max_lease_duration=1 * constants.MINUTES
        )

    def high_throughput(self: Self) -> FlowControl:
        return self.create(
            max_messages=1000,
            max_bytes=5 * constants.MEGABYTE,
            max_lease_duration=5 * constants.MINUTES
        )

    def aggressive(self: Self) -> FlowControl:
        return self.create(
            max_messages=5000,
            max_bytes=20 * constants.MEGABYTE,
            max_lease_duration=10 * constants.MINUTES
        )
