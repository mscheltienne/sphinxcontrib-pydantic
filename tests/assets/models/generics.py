"""Generic type models for testing."""

from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel

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
