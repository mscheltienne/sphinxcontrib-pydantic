"""Nested model structures for testing."""

from __future__ import annotations

from pydantic import BaseModel


class Address(BaseModel):
    """An address."""

    street: str
    city: str
    country: str = "USA"


class Person(BaseModel):
    """A person with an address."""

    name: str
    age: int
    address: Address


class Company(BaseModel):
    """A company with employees."""

    name: str
    headquarters: Address
    employees: list[Person] = []


class RecursiveModel(BaseModel):
    """A model that references itself."""

    name: str
    children: list[RecursiveModel] = []
