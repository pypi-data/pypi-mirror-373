import logging
from typing import Self

from snakestack.logging import get_request_id


class RequestIdFilter(logging.Filter):
    def filter(self: Self, record: logging.LogRecord) -> bool:
        record.request_id = get_request_id()
        return True

class ExcludeLoggerFilter(logging.Filter):
    def __init__(self: Self, excluded_name: list[str]) -> None:
        super().__init__()
        self.excluded = set(excluded_name)

    def filter(self: Self, record: logging.LogRecord) -> bool:
        return record.name not in self.excluded
