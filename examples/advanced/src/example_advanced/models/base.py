"""Base models demonstrating inheritance patterns."""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class BaseEntity(BaseModel):
    """Base class for all entities.

    This is the root of the entity hierarchy, providing common fields
    for identification and tracking.
    """

    id: int | None = Field(default=None, description="Unique identifier.")
    created_at: str | None = Field(default=None, description="Creation timestamp.")


class NamedEntity(BaseEntity):
    """Entity with a name.

    Extends BaseEntity with a required name field and validation.
    """

    name: str = Field(min_length=1, description="Entity name.")

    @field_validator("name")
    @classmethod
    def strip_name(cls, v: str) -> str:
        """Strip whitespace from name."""
        return v.strip()


class AuditableEntity(NamedEntity):
    """Entity with audit information.

    Extends NamedEntity with audit trail fields for tracking changes.
    """

    updated_at: str | None = Field(default=None, description="Last update timestamp.")
    updated_by: str | None = Field(default=None, description="User who last updated.")
