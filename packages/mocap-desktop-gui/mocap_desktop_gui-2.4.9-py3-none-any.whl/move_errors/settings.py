"""Settings required by move-errors."""
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class MoveErrorSettings(BaseSettings):
    """Settings required by move-errors."""

    service: str = Field(default="Move.ai")
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
