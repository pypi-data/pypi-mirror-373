from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class MongoDBSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SNAKESTACK_MONGODB_")

    uri: str = Field(
        default="mongodb://localhost:27017",
        description=""
    )

    dbname: str = Field(
        default="snakestack",
        description=""
    )
