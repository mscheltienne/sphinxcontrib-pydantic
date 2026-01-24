"""SQLModel table definitions.

Table models map directly to database tables and include
relationship definitions for ORM operations.
"""

from __future__ import annotations

from sqlmodel import Field, Relationship, SQLModel

from example_advanced.database.dto import ProjectBase


class User(SQLModel, table=True):
    """User table in the database.

    Represents application users who can own projects.
    """

    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True, description="Unique username.")
    email: str = Field(unique=True, description="User email.")

    projects: list[Project] = Relationship(back_populates="owner")


class Project(ProjectBase, table=True):
    """Project table in the database.

    Represents projects owned by users, inheriting from ProjectBase DTO.
    """

    id: int | None = Field(default=None, primary_key=True)
    owner_id: int = Field(foreign_key="user.id", description="Owner's user ID.")

    owner: User = Relationship(back_populates="projects")
