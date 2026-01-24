"""Generic type models for testing."""

from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel, field_validator

T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")


class GenericContainer(BaseModel, Generic[T]):
    """A generic container model."""

    value: T
    label: str = ""


class GenericMapping(BaseModel, Generic[K, V]):
    """A generic key-value model."""

    key: K
    value: V


class ConcreteContainer(GenericContainer[int]):
    """A concrete instantiation of GenericContainer."""

    multiplier: int = 1


class GenericWithValidator(BaseModel, Generic[T]):
    """Generic model with a validator."""

    data: T
    name: str = ""

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate name is trimmed."""
        return v.strip()


class ConcreteWithValidator(GenericWithValidator[str]):
    """Concrete generic with inherited validator."""

    extra: int = 0


class BoundedGeneric(BaseModel, Generic[T]):
    """Generic with validated items."""

    items: list[T]
    count: int = 0

    @field_validator("items")
    @classmethod
    def validate_items_not_empty(cls, v: list[T]) -> list[T]:
        """Ensure items list is not empty."""
        if not v:
            raise ValueError("items cannot be empty")
        return v
