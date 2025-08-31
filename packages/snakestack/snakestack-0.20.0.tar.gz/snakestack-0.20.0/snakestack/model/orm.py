from pydantic import BaseModel, ConfigDict


class ORMModel(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
        from_attributes=True
    )
