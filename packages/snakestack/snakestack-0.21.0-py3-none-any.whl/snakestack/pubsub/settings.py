from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class PubSubSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SNAKESTACK_PUBSUB_")
    project_id: str = Field(
        default="snakestack-project",
        description=""
    )
    subscription_name: str | None = Field(
        default=None,
        description=""
    )
    topic_name: str | None = Field(
        default=None,
        description=""
    )
