from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class LoggingSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SNAKESTACK_LOGGING_")

    level: str = Field(
        default="INFO",
        description="Logging level for the application (e.g., DEBUG, INFO, WARNING, ERROR)."
    )

    default_formatter: str = Field(
        default="default",
        description="Default formatter to be used in the logging configuration (e.g., default, custom_json, with_request_id)."
    )

    default_filters: str = Field(
        default="request_id",
        description="Comma-separated list of default filters to be applied to log records (e.g., request_id, excluded_name)."
    )

    filter_excluded_name: list[str] | None = Field(
        default=None,
        description="Logger name or pattern to exclude from logging output (e.g., 'exclude.me' to suppress logs from that logger)."
    )

    @field_validator("default_formatter")
    @classmethod
    def validate_log_formatter(cls, v: str) -> str:
        allowed = {"default", "custom_json", "with_request_id"}
        if v not in allowed:
            raise ValueError(f"Invalid formatter '{v}'. Must be one of: {', '.join(allowed)}.")
        return v

    @field_validator("default_filters")
    @classmethod
    def validate_log_filter(cls, v: str) -> str:
        allowed = ["request_id", "excluded_name"]
        if not all([item in allowed for item in v.split(",")]):
            raise ValueError(f"Invalid filter '{v}'. Must be one of: {', '.join(allowed)}.")
        return v

    @field_validator("filter_excluded_name", mode="before")
    @classmethod
    def _coerce_excluded_names(cls, v: Any) -> list[str]:
        if v is None or v == "":
            return []

        if isinstance(v, str):
            parts = [p.strip() for p in v.split(",")]
            return [p for p in parts if p]

        raise TypeError(
            "Invalid excluded name filter. Must be a comma-separated string"
        )
