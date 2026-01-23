"""Computed field models for testing."""

from __future__ import annotations

from functools import cached_property

from pydantic import BaseModel, computed_field


class ComputedFieldModel(BaseModel):
    """Model with computed field."""

    first_name: str
    last_name: str

    @computed_field
    @cached_property
    def full_name(self) -> str:
        """The full name (computed)."""
        return f"{self.first_name} {self.last_name}"


class ComputedWithDescription(BaseModel):
    """Model with documented computed field."""

    width: float
    height: float

    @computed_field(description="The area of the rectangle.")
    @property
    def area(self) -> float:
        """Calculate the area."""
        return self.width * self.height
