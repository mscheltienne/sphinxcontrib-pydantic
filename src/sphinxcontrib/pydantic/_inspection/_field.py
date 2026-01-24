"""Field inspection utilities for Pydantic v2 models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from pydantic_core import PydanticUndefined

from pydantic import BaseModel
from sphinxcontrib.pydantic._inspection._model import is_pydantic_model

if TYPE_CHECKING:
    from typing import Any


# Constraint attributes to extract from field metadata
_CONSTRAINT_ATTRS = frozenset(
    {
        "ge",
        "gt",
        "le",
        "lt",
        "multiple_of",
        "strict",
        "min_length",
        "max_length",
        "pattern",
        "max_digits",
        "decimal_places",
    }
)


@dataclass(frozen=True, slots=True)
class FieldInfo:
    """Information about a Pydantic model field.

    Attributes
    ----------
    name : str
        The name of the field.
    annotation : type | Any
        The type annotation of the field.
    default : Any
        The default value of the field, or PydanticUndefinedType if none.
    has_default : bool
        Whether the field has a default value.
    has_default_factory : bool
        Whether the field has a default_factory.
    is_required : bool
        Whether the field is required.
    alias : str | None
        The field alias, if any.
    description : str | None
        The field description, if any.
    title : str | None
        The field title, if any.
    examples : list[Any] | None
        Example values for the field, if any.
    constraints : dict[str, Any]
        Constraints on the field (ge, le, pattern, etc.).
    """

    name: str
    annotation: type | Any
    default: Any = field(repr=False)
    has_default: bool = False
    has_default_factory: bool = False
    is_required: bool = True
    alias: str | None = None
    description: str | None = None
    title: str | None = None
    examples: list[Any] | None = field(default=None, repr=False)
    constraints: dict[str, Any] = field(default_factory=dict)


def get_field_info(model: type[BaseModel], field_name: str) -> FieldInfo:
    """Extract information about a specific field from a Pydantic model.

    Parameters
    ----------
    model : type[BaseModel]
        The Pydantic model class.
    field_name : str
        The name of the field to inspect.

    Returns
    -------
    FieldInfo
        Information about the field.

    Raises
    ------
    TypeError
        If the provided object is not a Pydantic model class.
    KeyError
        If the field does not exist in the model.
    """
    if not is_pydantic_model(model):
        raise TypeError(f"{model!r} is not a Pydantic model class.")

    if field_name not in model.model_fields:
        raise KeyError(f"Field '{field_name}' does not exist in model {model.__name__}")

    pydantic_field = model.model_fields[field_name]

    # Get annotation
    annotation = pydantic_field.annotation

    # Get default value
    default = pydantic_field.default
    has_default = default is not PydanticUndefined

    # Check for default_factory
    has_default_factory = pydantic_field.default_factory is not None

    # Use Pydantic's built-in is_required check
    is_required = pydantic_field.is_required()

    # Get alias
    alias = pydantic_field.alias

    # Get description
    description = pydantic_field.description

    # Get title
    title = pydantic_field.title

    # Get examples
    examples = pydantic_field.examples

    # Extract constraints from metadata
    constraints = _extract_constraints(pydantic_field)

    return FieldInfo(
        name=field_name,
        annotation=annotation,
        default=default,
        has_default=has_default,
        has_default_factory=has_default_factory,
        is_required=is_required,
        alias=alias,
        description=description,
        title=title,
        examples=list(examples) if examples else None,
        constraints=constraints,
    )


def _extract_constraints(pydantic_field: Any) -> dict[str, Any]:
    """Extract constraints from a Pydantic field.

    Parameters
    ----------
    pydantic_field : FieldInfo
        The Pydantic FieldInfo object.

    Returns
    -------
    dict[str, Any]
        Dictionary of constraints.
    """
    constraints: dict[str, Any] = {}

    # Check metadata for constraint annotations
    for meta in pydantic_field.metadata:
        for attr in _CONSTRAINT_ATTRS:
            if hasattr(meta, attr):
                value = getattr(meta, attr)
                if value is not None:
                    constraints[attr] = value

    return constraints
