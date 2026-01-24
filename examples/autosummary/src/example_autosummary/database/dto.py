"""Data Transfer Objects (DTOs) for the database models.

These DTOs define the core data schema (i.e. the columns) without persistence details
such as table mapping or relationships. The table classes in table.py inherit from
these DTOs.
"""

# do not use 'from __future__ import annotations' in a model-definition file as this is
# not supported by SQLModel and SQLAlchemy.

from datetime import UTC, datetime

from pydantic import ConfigDict
from sqlmodel import Field, SQLModel


class UserDTO(SQLModel):
    """Data Transfer Object for the User table.

    Stores user account information with timestamps.
    """

    id: int | None = Field(default=None, description="Primary key.")
    username: str = Field(description="Unique username.")
    email: str = Field(description="Email address.")
    hashed_password: str = Field(description="Hashed password.")
    is_active: bool = Field(default=True, description="Whether the user is active.")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Creation timestamp.",
    )
    updated_at: datetime | None = Field(default=None, description="Last update time.")

    model_config = ConfigDict(frozen=True)
