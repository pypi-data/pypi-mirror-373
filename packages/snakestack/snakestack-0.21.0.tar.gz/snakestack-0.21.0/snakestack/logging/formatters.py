from datetime import UTC, datetime
from logging import Formatter, LogRecord
from typing import Any, Self

import orjson

from snakestack.logging.encoders import safe_jsonable_encoder


class JsonFormatter(Formatter):
    def format(
        self: Self,
        record: LogRecord,
        *args: Any,
        **kwargs: Any
    ) -> str:
        Formatter.format(self, record)
        return orjson.dumps(
            self._create_log(record),
            default=safe_jsonable_encoder
        ).decode("utf-8")

    def _create_log(self: Self, record: LogRecord) -> dict[str, Any]:
        message: dict[str, Any] = {
            "time": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "level": record.levelname,
            "pid": record.process,
            "name": f"{record.name}:{record.lineno}",
            "msg": record.getMessage(),
            "request": {}
        }

        if record.exc_info:
            message["exc_info"] = str(record.exc_info)

        if hasattr(record, "request_id") and record.request_id:
            message["request"].update({"id": record.request_id})

        if hasattr(record, "otelTraceID") and record.otelTraceID:
            message["request"].update({"trace_id": record.otelTraceID})

        if hasattr(record, "otelSpanID") and record.otelSpanID:
            message["request"].update({"span_id": record.otelSpanID})

        return message
