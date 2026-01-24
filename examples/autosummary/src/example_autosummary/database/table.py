"""SQLModel table definitions.

The tables define the relationship and constraints between the columns defined in the
Data Transfer Objects (DTOs).
"""

# do not use 'from __future__ import annotations' in a model-definition file as this is
# not supported by SQLModel and SQLAlchemy.

from pydantic import ConfigDict
from sqlmodel import Field

from example_autosummary.database import dto


class UserTable(dto.UserDTO, table=True):
    """User table in the database.

    Stores user account information with timestamps.
    """

    __tablename__ = "user"

    id: int | None = Field(default=None, primary_key=True, description="Primary key.")
    username: str = Field(index=True, unique=True, description="Unique username.")
    email: str = Field(index=True, unique=True, description="Email address.")

    model_config = ConfigDict(frozen=False)
