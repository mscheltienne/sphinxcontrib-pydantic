"""Validator patterns demonstration."""

from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator


class PasswordReset(BaseModel):
    """Password reset with model validator.

    Demonstrates after-mode model validation to ensure field consistency.
    """

    password: str = Field(min_length=8, description="New password.")
    confirm_password: str = Field(description="Password confirmation.")

    @model_validator(mode="after")
    def passwords_match(self) -> PasswordReset:
        """Ensure passwords match."""
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self


class DataProcessor(BaseModel):
    """Model with before-mode validator.

    Demonstrates pre-processing of input data before validation.
    """

    data: dict[str, Any] = Field(description="Data to process.")

    @model_validator(mode="before")
    @classmethod
    def ensure_dict(cls, values: Any) -> dict[str, Any]:
        """Ensure input is a dictionary.

        Parses JSON strings into dictionaries if needed.
        """
        if isinstance(values, str):
            return {"data": json.loads(values)}
        return values


class BoundedValue(BaseModel):
    """Model with multiple field validators.

    Demonstrates validation applied to multiple fields simultaneously.
    """

    x: float = Field(description="X coordinate.")
    y: float = Field(description="Y coordinate.")
    z: float = Field(description="Z coordinate.")

    @field_validator("x", "y", "z")
    @classmethod
    def clamp_values(cls, v: float) -> float:
        """Clamp values to [-1, 1] range."""
        return max(-1.0, min(1.0, v))
