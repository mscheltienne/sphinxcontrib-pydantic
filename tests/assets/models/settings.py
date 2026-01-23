"""BaseSettings models for testing."""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class SimpleSettings(BaseSettings):
    """Simple settings model."""

    debug: bool = False
    log_level: str = "INFO"


class SettingsWithEnvPrefix(BaseSettings):
    """Settings with environment variable prefix."""

    model_config = SettingsConfigDict(env_prefix="MYAPP_")

    api_key: str
    api_url: str = "https://api.example.com"


class NestedSettings(BaseSettings):
    """Settings with nested configuration."""

    app_name: str = Field(default="MyApp")
    database_url: str
    cache_ttl: int = 300
