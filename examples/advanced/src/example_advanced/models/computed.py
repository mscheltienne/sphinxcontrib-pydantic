"""Computed field examples."""

from __future__ import annotations

from functools import cached_property

from pydantic import BaseModel, Field, computed_field


class Rectangle(BaseModel):
    """Rectangle with computed area and perimeter.

    Demonstrates computed fields that derive values from other fields.
    """

    width: float = Field(gt=0, description="Rectangle width.")
    height: float = Field(gt=0, description="Rectangle height.")

    @computed_field
    @property
    def area(self) -> float:
        """Calculate the area."""
        return self.width * self.height

    @computed_field
    @property
    def perimeter(self) -> float:
        """Calculate the perimeter."""
        return 2 * (self.width + self.height)


class Person(BaseModel):
    """Person with computed full name.

    Demonstrates cached computed fields for expensive operations.
    """

    first_name: str = Field(description="First name.")
    last_name: str = Field(description="Last name.")
    birth_year: int = Field(description="Year of birth.")

    @computed_field
    @cached_property
    def full_name(self) -> str:
        """Get the full name."""
        return f"{self.first_name} {self.last_name}"
