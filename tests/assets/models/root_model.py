"""Test models for RootModel support."""

from __future__ import annotations

from pydantic import RootModel, field_validator


class IntList(RootModel[list[int]]):
    """A list of integers."""


class StringMapping(RootModel[dict[str, str]]):
    """A string-to-string mapping."""


class ConstrainedIntList(RootModel[list[int]]):
    """A list of integers with validation.

    Only accepts lists of positive integers.
    """

    @field_validator("root")
    @classmethod
    def check_positive(cls, v: list[int]) -> list[int]:
        """Ensure all integers are positive."""
        if any(x <= 0 for x in v):
            raise ValueError("All integers must be positive")
        return v


class NestedModel(RootModel[list[IntList]]):
    """A nested RootModel containing lists of IntList."""
