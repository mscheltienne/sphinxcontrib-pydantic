"""SQLModel DTO (Data Transfer Object) models.

DTOs are used to transfer data between layers of the application,
providing validation without database table mapping.
"""

from __future__ import annotations

from sqlmodel import Field, SQLModel


class ProjectBase(SQLModel):
    """Base project fields shared by all project models.

    Contains the core fields that are common across create, read,
    and update operations.
    """

    name: str = Field(min_length=1, max_length=100, description="Project name.")
    description: str | None = Field(default=None, description="Project description.")


class ProjectCreate(ProjectBase):
    """Model for creating a new project.

    Extends ProjectBase with fields required for project creation.
    """

    owner_id: int = Field(description="ID of the project owner.")


class ProjectRead(ProjectBase):
    """Model for reading project data.

    Extends ProjectBase with fields populated from the database.
    """

    id: int = Field(description="Project ID.")
    owner_id: int = Field(description="Owner ID.")


class ProjectUpdate(SQLModel):
    """Model for updating a project.

    All fields are optional to support partial updates.
    """

    name: str | None = Field(default=None, description="New project name.")
    description: str | None = Field(default=None, description="New description.")
