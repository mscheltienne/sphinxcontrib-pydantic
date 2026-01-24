"""Nested configuration models demonstrating composed Pydantic models."""

from __future__ import annotations

from functools import cached_property
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, computed_field


class DatabaseConfig(BaseModel):
    """Database connection configuration.

    Provides all necessary settings for connecting to a PostgreSQL database.
    """

    host: str = Field(default="localhost", description="Database host.")
    port: int = Field(default=5432, ge=1, le=65535, description="Database port.")
    name: str = Field(description="Database name.")
    user: str = Field(description="Database user.")
    password: str = Field(description="Database password.")

    @computed_field
    @cached_property
    def connection_string(self) -> str:
        """Generate the connection string.

        Constructs a PostgreSQL connection URL from the configuration values.
        """
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


class CacheConfig(BaseModel):
    """Cache configuration.

    Settings for the application's caching layer.
    """

    enabled: bool = Field(default=True, description="Whether caching is enabled.")
    ttl: int = Field(default=3600, ge=0, description="Cache TTL in seconds.")
    backend: str = Field(default="memory", description="Cache backend type.")


class AppConfig(BaseModel):
    """Main application configuration with nested configs.

    This model demonstrates composition of multiple configuration models
    into a single cohesive configuration object.
    """

    model_config = ConfigDict(extra="allow")

    app_name: str = Field(description="Application name.")
    debug: bool = Field(default=False, description="Enable debug mode.")
    database: DatabaseConfig = Field(description="Database configuration.")
    cache: CacheConfig = Field(
        default_factory=CacheConfig, description="Cache settings."
    )
    extra_settings: dict[str, Any] = Field(
        default_factory=dict, description="Extra settings."
    )
