"""BaseSettings configuration examples.

Settings models load configuration from environment variables,
providing type-safe access to external configuration.
"""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """Application settings loaded from environment.

    These settings are loaded from environment variables with the prefix ``APP_``.

    Examples
    --------
    Set environment variables::

        export APP_NAME="MyApp"
        export APP_DEBUG="true"
        export APP_SECRET_KEY="my-secret-key"
    """

    model_config = SettingsConfigDict(env_prefix="APP_")

    name: str = Field(default="MyApp", description="Application name.")
    debug: bool = Field(default=False, description="Enable debug mode.")
    log_level: str = Field(default="INFO", description="Logging level.")
    secret_key: str = Field(
        default="changeme", description="Secret key for encryption."
    )


class DatabaseSettings(BaseSettings):
    """Database settings from environment.

    Settings for database connection loaded from environment variables
    with the prefix ``DB_``.

    Examples
    --------
    Set environment variables::

        export DB_HOST="localhost"
        export DB_PORT="5432"
        export DB_NAME="myapp"
        export DB_USER="postgres"
        export DB_PASSWORD="secret"
    """

    model_config = SettingsConfigDict(env_prefix="DB_")

    host: str = Field(default="localhost", description="Database host.")
    port: int = Field(default=5432, description="Database port.")
    name: str = Field(default="app", description="Database name.")
    user: str = Field(default="postgres", description="Database user.")
    password: str = Field(default="changeme", description="Database password.")
