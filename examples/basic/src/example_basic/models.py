"""Basic Pydantic models for documentation demonstration."""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class User(BaseModel):
    """A simple user model.

    This model demonstrates basic field types with documentation.
    """

    name: str = Field(description="The user's full name.")
    email: str = Field(description="The user's email address.")
    age: int = Field(default=0, ge=0, description="The user's age in years.")
    is_active: bool = Field(default=True, description="Whether the user is active.")


class Product(BaseModel):
    """A product in the catalog.

    Demonstrates field constraints and aliases.
    """

    id: int = Field(description="Unique product identifier.")
    name: str = Field(min_length=1, max_length=100, description="Product name.")
    price: float = Field(gt=0, description="Price in dollars.")
    sku: str = Field(alias="SKU", description="Stock keeping unit.")
    in_stock: bool = Field(default=True)


class Order(BaseModel):
    """An order with validation.

    Demonstrates field validators.
    """

    order_id: str = Field(description="Unique order identifier.")
    quantity: int = Field(ge=1, le=100, description="Number of items.")
    total: float = Field(ge=0, description="Total price.")

    @field_validator("order_id")
    @classmethod
    def validate_order_id(cls, v: str) -> str:
        """Ensure order ID starts with 'ORD-'."""
        if not v.startswith("ORD-"):
            raise ValueError("Order ID must start with 'ORD-'")
        return v
