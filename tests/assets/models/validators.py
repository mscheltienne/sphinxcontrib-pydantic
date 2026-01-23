"""Validator models for testing."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, field_validator, model_validator

if TYPE_CHECKING:
    from typing import Any


class SingleFieldValidator(BaseModel):
    """Model with single field validator."""

    value: int

    @field_validator("value")
    @classmethod
    def check_positive(cls, v: int) -> int:
        """Ensure value is positive."""
        if v < 0:
            raise ValueError("must be positive")
        return v


class MultiFieldValidator(BaseModel):
    """Model with validator on multiple fields."""

    x: int
    y: int

    @field_validator("x", "y")
    @classmethod
    def check_bounds(cls, v: int) -> int:
        """Ensure values are within bounds."""
        if not 0 <= v <= 100:
            raise ValueError("must be 0-100")
        return v


class BeforeValidator(BaseModel):
    """Model with before-mode validator."""

    value: int

    @field_validator("value", mode="before")
    @classmethod
    def coerce_string(cls, v: int | str) -> int:
        """Coerce string to int."""
        if isinstance(v, str):
            return int(v)
        return v


class ModelValidatorAfter(BaseModel):
    """Model with after-mode model validator."""

    password: str
    confirm: str

    @model_validator(mode="after")
    def passwords_match(self) -> ModelValidatorAfter:
        """Ensure passwords match."""
        if self.password != self.confirm:
            raise ValueError("passwords must match")
        return self


class ModelValidatorBefore(BaseModel):
    """Model with before-mode model validator."""

    data: dict[str, Any]

    @model_validator(mode="before")
    @classmethod
    def ensure_dict(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Ensure input is a dict."""
        if not isinstance(values, dict):
            raise ValueError("must be dict")
        return values
