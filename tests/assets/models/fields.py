"""Field variation models for testing."""

from __future__ import annotations

from pydantic import BaseModel, Field, PositiveInt


class FieldWithAlias(BaseModel):
    """Model with aliased field."""

    internal_name: str = Field(alias="externalName")


class FieldWithConstraints(BaseModel):
    """Model with constrained fields."""

    positive: PositiveInt
    bounded: int = Field(ge=0, le=100)
    length_bounded: str = Field(min_length=1, max_length=50)
    pattern_field: str = Field(pattern=r"^[a-z]+$")


class FieldWithDefaults(BaseModel):
    """Model with various default types."""

    required_field: str
    optional_field: str | None = None
    default_value: int = 42
    factory_default: list[str] = Field(default_factory=list)


class FieldWithMetadata(BaseModel):
    """Model with field metadata."""

    documented: str = Field(description="A documented field.")
    titled: str = Field(title="Titled Field")
    example_field: str = Field(examples=["example1", "example2"])
