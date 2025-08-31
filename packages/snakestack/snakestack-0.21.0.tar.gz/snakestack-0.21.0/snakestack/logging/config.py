import logging
import logging.config
from typing import Any


def setup_logging(
    logging_config: dict[str, Any] | None = None,
    log_level: str = "INFO",
    filter_excluded_name: list[str] | None = None,
    default_formatter: str = "default",
    default_filter: str = "request_id"
) -> None:
    if filter_excluded_name is None:
        filter_excluded_name = []

    default_filters: dict[str, Any] = {
        "request_id": {"()": "snakestack.logging.filters.RequestIdFilter"},
        "excluded_name": {
            "()": "snakestack.logging.filters.ExcludeLoggerFilter",
            "excluded_name": filter_excluded_name
        }
    }

    default_handlers: dict[str, Any] = {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": default_formatter,
            "filters": default_filter.split(","),
        }
    }

    default_formatters: dict[str, Any] = {
        "default": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        },
        "with_request_id": {
            "format": (
                "%(asctime)s [%(levelname)s] [req_id=%(request_id)s] "
                "%(name)s: %(message)s"
            )
        },
        "custom_json": {
            "()": "snakestack.logging.formatters.JsonFormatter"
        }
    }

    default_logging_config: dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": default_formatters,
        "handlers": default_handlers,
        "filters": default_filters,
        "root": {
            "level": log_level,
            "handlers": ["console"]
        }
    }

    logging.config.dictConfig(logging_config or default_logging_config)
