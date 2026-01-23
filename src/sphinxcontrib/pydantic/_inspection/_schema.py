"""JSON schema generation utilities for Pydantic models."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from sphinx.util import logging

if TYPE_CHECKING:
    from typing import Any

    from pydantic import BaseModel

_logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class SchemaInfo:
    """Information about a JSON schema.

    Attributes
    ----------
    schema : dict[str, Any]
        The JSON schema dictionary.
    title : str | None
        The schema title, if any.
    description : str | None
        The schema description, if any.
    properties : dict[str, Any]
        The schema properties.
    required : tuple[str, ...]
        Names of required properties.
    definitions : dict[str, Any]
        Nested schema definitions (for $defs).
    """

    schema: dict[str, Any]
    title: str | None
    description: str | None
    properties: dict[str, Any]
    required: tuple[str, ...]
    definitions: dict[str, Any]


def get_schema_info(model: type[BaseModel]) -> SchemaInfo:
    """Extract JSON schema information from a Pydantic model.

    Parameters
    ----------
    model : type[BaseModel]
        The Pydantic model class.

    Returns
    -------
    SchemaInfo
        Information about the model's JSON schema.

    Raises
    ------
    ValueError
        If the schema cannot be generated.
    """
    try:
        schema = model.model_json_schema()
    except Exception as e:
        raise ValueError(f"Failed to generate JSON schema for {model}: {e}") from e

    return SchemaInfo(
        schema=schema,
        title=schema.get("title"),
        description=schema.get("description"),
        properties=schema.get("properties", {}),
        required=tuple(schema.get("required", [])),
        definitions=schema.get("$defs", {}),
    )


def generate_json_schema(
    model: type[BaseModel],
    *,
    indent: int = 2,
    sort_keys: bool = False,
) -> str:
    """Generate a formatted JSON schema string for a Pydantic model.

    Parameters
    ----------
    model : type[BaseModel]
        The Pydantic model class.
    indent : int, optional
        Indentation level for JSON formatting, by default 2.
    sort_keys : bool, optional
        Whether to sort keys in the output, by default False.

    Returns
    -------
    str
        The formatted JSON schema string.

    Raises
    ------
    ValueError
        If the schema cannot be generated.
    """
    import json

    try:
        schema = model.model_json_schema()
        return json.dumps(schema, indent=indent, sort_keys=sort_keys)
    except Exception as e:
        raise ValueError(f"Failed to generate JSON schema for {model}: {e}") from e
