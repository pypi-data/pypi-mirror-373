from pydantic import BaseModel, ConfigDict, Field

from snakestack import constants


class ErrorModel(BaseModel):
    model_config = ConfigDict(
        extra='allow',
        str_strip_whitespace=True,
        str_min_length=1,
        frozen=True
    )
    detail: str = Field(..., description=constants.ERROR_DETAIL_SCHEMA_DESCRIPTION)
