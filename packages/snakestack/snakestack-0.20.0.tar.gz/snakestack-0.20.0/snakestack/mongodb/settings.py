from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class MongoDBSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SNAKESTACK_MONGODB_")

    host: str = Field(
        default="mongodb://localhost:27017",
        description=""
    )
    port: int = Field(
        default=27017,
        description=""
    )
    username: str | None = Field(
        default=None,
        description=""
    )
    password: str | None = Field(
        default=None,
        description=""
    )
    auth_source: str = Field(
        default="admin",
        description=""
    )
    dbname: str = Field(
        default="snakestack",
        description=""
    )
