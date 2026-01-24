"""Generic model examples.

Generic models provide reusable patterns that work with
different types while maintaining type safety.
"""

from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")


class Response(BaseModel, Generic[T]):
    """Generic API response wrapper.

    A standard response envelope for API endpoints that wraps
    the actual response data with status information.
    """

    success: bool = Field(description="Whether the request succeeded.")
    data: T | None = Field(default=None, description="Response data.")
    error: str | None = Field(default=None, description="Error message if failed.")


class PaginatedResponse(Response[T], Generic[T]):
    """Paginated response with metadata.

    Extends the basic Response with pagination information
    for list endpoints.
    """

    page: int = Field(ge=1, description="Current page number.")
    per_page: int = Field(ge=1, le=100, description="Items per page.")
    total: int = Field(ge=0, description="Total number of items.")


class KeyValueStore(BaseModel, Generic[K, V]):
    """Generic key-value store.

    A simple container for storing and retrieving values by key,
    parameterized by key and value types.
    """

    items: dict[K, V] = Field(default_factory=dict, description="Stored items.")

    def get(self, key: K, default: V | None = None) -> V | None:
        """Get a value by key.

        Parameters
        ----------
        key : K
            The key to look up.
        default : V | None
            Default value if key not found.

        Returns
        -------
        V | None
            The value if found, otherwise the default.
        """
        return self.items.get(key, default)
