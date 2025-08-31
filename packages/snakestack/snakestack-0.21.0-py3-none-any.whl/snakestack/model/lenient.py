from pydantic import BaseModel, ConfigDict


class LenientModel(BaseModel):
    model_config = ConfigDict(
        extra='allow',
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )
