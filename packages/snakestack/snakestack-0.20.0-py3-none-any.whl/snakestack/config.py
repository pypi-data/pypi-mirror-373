from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from snakestack import version
from snakestack.cache.settings import CacheSettings
from snakestack.logging.settings import LoggingSettings
from snakestack.mongodb.settings import MongoDBSettings
from snakestack.pubsub.settings import PubSubSettings
from snakestack.telemetry.settings import OtelSettings


class SnakeStackSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="SNAKESTACK_APP_",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
    )

    app_version: str = Field(
        default=version.__version__,
        description=""
    )

    cache: CacheSettings = Field(default_factory=CacheSettings)
    log: LoggingSettings = Field(default_factory=LoggingSettings)
    mongo: MongoDBSettings = Field(default_factory=MongoDBSettings)
    pubsub: PubSubSettings = Field(default_factory=PubSubSettings)
    otel: OtelSettings = Field(default_factory=OtelSettings)


@lru_cache
def get_settings() -> SnakeStackSettings:
    return SnakeStackSettings()


settings = get_settings()
