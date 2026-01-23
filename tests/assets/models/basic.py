"""Basic Pydantic model variations for testing."""

from __future__ import annotations

from pydantic import BaseModel, Field


class EmptyModel(BaseModel):
    """Model with no fields."""


class SimpleModel(BaseModel):
    """Model with basic fields.

    A simple model demonstrating basic field types.
    """

    name: str
    count: int = 0


class DocumentedModel(BaseModel):
    """Model with documented fields.

    This model demonstrates field documentation via Field(description=...).
    """

    name: str = Field(description="The name of the item.")
    value: int = Field(default=0, description="A numeric value.")


class ModelWithDocstrings(BaseModel):
    """Model with attribute docstrings.

    Fields can be documented with attribute docstrings.
    """

    name: str
    """The name field with docstring."""

    value: int = 0
    """The value field with default."""
