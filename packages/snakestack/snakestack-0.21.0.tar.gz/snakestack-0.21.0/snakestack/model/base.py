from pydantic import BaseModel, ConfigDict


class StrictModel(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
        populate_by_name=True,
        validate_assignment=True,
        str_strip_whitespace=True,
        str_min_length=1
    )
