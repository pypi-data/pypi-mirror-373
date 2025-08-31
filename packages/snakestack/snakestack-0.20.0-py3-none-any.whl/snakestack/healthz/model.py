from pydantic import Field

from snakestack import constants
from snakestack.model import StrictModel


class CheckModel(StrictModel):
    ok: bool = Field(..., description=constants.SCHEMA_CHECK_OK_DESCRIPTION)
    latency_ms: float = Field(
        ..., description=constants.SCHEMA_CHECK_LATENCY_MS_DESCRIPTION
    )
    error: str | None = Field(
        default=None, description=constants.SCHEMA_CHECK_ERROR_DESCRIPTION
    )


class HealthCheckModel(StrictModel):
    service_name: str = Field(
        ..., description=constants.SCHEMA_HEALTHZ_SERVICE_NAME_DESCRIPTION
    )
    version: str = Field(
        ..., description=constants.SCHEMA_HEALTHZ_VERSION_DESCRIPTION
    )
    host: str = Field(..., description=constants.SCHEMA_HEALTHZ_HOST_DESCRIPTION)
    uptime: str | None = Field(
        default=None, description=constants.SCHEMA_HEALTHZ_UPTIME_DESCRIPTION
    )
    timestamp: str = Field(
        ..., description=constants.SCHEMA_HEALTHZ_TIMESTAMP_DESCRIPTION
    )
    environment: str = Field(
        ..., description=constants.SCHEMA_HEALTHZ_ENVIRONMENT_DESCRIPTION
    )
    status: bool = Field(
        ..., description=constants.SCHEMA_HEALTHZ_STATUS_DESCRIPTION
    )
    latency_ms: float = Field(
        ..., description=constants.SCHEMA_HEALTHZ_LATENCY_MS_DESCRIPTION
    )
    details: dict[str, CheckModel] = Field(
        ..., description=constants.SCHEMA_HEALTHZ_DETAILS_DESCRIPTION
    )
