"""Inheritance test models."""

from __future__ import annotations

from pydantic import BaseModel, field_validator, model_validator


class BaseModelWithValidator(BaseModel):
    """Base model with a validator."""

    base_field: str
    """Field defined on base class."""

    @field_validator("base_field")
    @classmethod
    def validate_base_field(cls, v: str) -> str:
        """Validate base_field is non-empty."""
        if not v:
            raise ValueError("must not be empty")
        return v


class ChildModelSimple(BaseModelWithValidator):
    """Child model that inherits validator."""

    child_field: int
    """Field defined on child class."""


class ChildModelWithOwnValidator(BaseModelWithValidator):
    """Child model with its own validator."""

    child_field: int
    """Field defined on child class."""

    @field_validator("child_field")
    @classmethod
    def validate_child_field(cls, v: int) -> int:
        """Validate child_field is positive."""
        if v < 0:
            raise ValueError("must be positive")
        return v


class ChildModelOverrideValidator(BaseModelWithValidator):
    """Child model that overrides parent validator."""

    @field_validator("base_field")
    @classmethod
    def validate_base_field(cls, v: str) -> str:
        """Override parent validation - allow empty."""
        return v


class GrandchildModel(ChildModelWithOwnValidator):
    """Three levels of inheritance."""

    grandchild_field: float
    """Field on grandchild."""

    @field_validator("grandchild_field")
    @classmethod
    def validate_grandchild(cls, v: float) -> float:
        """Validate grandchild field."""
        return abs(v)


class BaseWithModelValidator(BaseModel):
    """Base model with model validator."""

    a: str
    b: str

    @model_validator(mode="after")
    def validate_ab(self) -> BaseWithModelValidator:
        """Validate a and b together."""
        if self.a == self.b:
            raise ValueError("a and b must be different")
        return self


class ChildWithInheritedModelValidator(BaseWithModelValidator):
    """Child inherits model validator."""

    c: int
