from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class CacheSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SNAKESTACK_CACHE_")
    host: str = Field(
        default="localhost",
        description=""
    )
    port: int = Field(
        default=6379,
        description=""
    )
    db: int = Field(
        default=0,
        description=""
    )
    password: str | None = Field(
        default=None,
        description=""
    )
