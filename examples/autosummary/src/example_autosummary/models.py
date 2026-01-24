"""Pydantic models for the application."""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class UserConfig(BaseModel):
    """User configuration model.

    Stores user preferences and settings for the application.
    """

    username: str = Field(min_length=3, max_length=50, description="Username.")
    email: str = Field(description="Email address.")
    theme: str = Field(default="light", description="UI theme preference.")
    notifications: bool = Field(default=True, description="Enable notifications.")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate email format."""
        if "@" not in v:
            raise ValueError("Invalid email format")
        return v.lower()


class DatabaseConfig(BaseModel):
    """Database connection configuration.

    Settings for connecting to the database backend.
    """

    host: str = Field(default="localhost", description="Database host.")
    port: int = Field(default=5432, ge=1, le=65535, description="Database port.")
    name: str = Field(description="Database name.")
    user: str = Field(description="Database user.")
    password: str = Field(description="Database password.")


class AppConfig(BaseModel):
    """Application configuration.

    Top-level configuration combining user and database settings.
    """

    debug: bool = Field(default=False, description="Enable debug mode.")
    log_level: str = Field(default="INFO", description="Logging level.")
    user: UserConfig = Field(description="User configuration.")
    database: DatabaseConfig = Field(description="Database configuration.")
