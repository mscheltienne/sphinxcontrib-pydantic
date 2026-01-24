"""Forward reference test models."""

from __future__ import annotations

from pydantic import BaseModel, field_validator


class SelfReferencing(BaseModel):
    """Model that references itself."""

    name: str
    parent: SelfReferencing | None = None
    children: list[SelfReferencing] = []

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate name is non-empty."""
        if not v.strip():
            raise ValueError("name must not be empty")
        return v.strip()


class NodeA(BaseModel):
    """First node in circular reference."""

    value: str
    b_ref: NodeB | None = None


class NodeB(BaseModel):
    """Second node in circular reference."""

    value: int
    a_ref: NodeA | None = None


# Update forward references
NodeA.model_rebuild()
NodeB.model_rebuild()


class StringAnnotationModel(BaseModel):
    """Model using string annotations throughout."""

    related: StringAnnotationModel | None = None
    items: list[str] = []

    @field_validator("items")
    @classmethod
    def validate_items(cls, v: list[str]) -> list[str]:
        """Validate items."""
        return [item.strip() for item in v]


class TreeNode(BaseModel):
    """Tree structure with self-reference."""

    value: int
    left: TreeNode | None = None
    right: TreeNode | None = None

    @field_validator("value")
    @classmethod
    def validate_positive(cls, v: int) -> int:
        """Value must be positive."""
        if v < 0:
            raise ValueError("must be positive")
        return v
