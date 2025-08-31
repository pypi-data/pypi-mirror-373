from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class OtelSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SNAKESTACK_OTEL_")

    disabled: bool = Field(
        default=False,
        description=(
            "Disables only the OpenTelemetry instrumentation provided by the SnakeStack library. "
            "This allows external OpenTelemetry configurations (e.g., opentelemetry-bootstrap or custom distro) "
            "to take full control over instrumentation without duplication. "
            "Equivalent to setting the environment variable SNAKESTACK_OTEL_DISABLED=true."
        )
    )
