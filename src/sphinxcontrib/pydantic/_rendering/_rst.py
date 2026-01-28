"""RST generation utilities for Pydantic documentation."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from sphinx.util.typing import restify, stringify_annotation

if TYPE_CHECKING:
    from typing import Any


def format_type_annotation(annotation: Any, *, as_rst: bool = False) -> str:
    """Format a type annotation for display.

    Uses Sphinx's stringify_annotation for plain text or restify for RST
    with cross-reference roles.

    Parameters
    ----------
    annotation : Any
        The type annotation to format.
    as_rst : bool
        If True, return RST with cross-reference roles (using restify).
        If False, return plain text (using stringify_annotation).

    Returns
    -------
    str
        The formatted type annotation string.
    """
    if annotation is None:
        return ":py:obj:`None`" if as_rst else "None"
    if as_rst:
        return restify(annotation, mode="smart")
    return stringify_annotation(annotation, mode="smart")


def format_default_value(value: Any) -> str:
    """Format a default value for display.

    Parameters
    ----------
    value : Any
        The default value to format.

    Returns
    -------
    str
        The formatted default value string.
    """
    if value is None:
        return "None"
    # Must check bool before int since bool is a subclass of int
    if isinstance(value, bool):
        return str(value)
    if isinstance(value, (int, float)):
        return str(value)
    # Handles str, list, tuple, dict, set, and everything else
    return repr(value)


def generate_json_schema_block(model: type) -> list[str]:
    """Generate RST lines for a JSON schema code block.

    Parameters
    ----------
    model : type
        The Pydantic model class.

    Returns
    -------
    list[str]
        RST lines for the JSON schema block, or empty list on error.
    """
    try:
        schema = model.model_json_schema()
        schema_str = json.dumps(schema, indent=2)

        lines = ["", "**JSON Schema:**", "", ".. code-block:: json", ""]
        # Indent each line of the schema for the code block
        lines.extend(f"   {line}" for line in schema_str.split("\n"))
        lines.append("")
        return lines
    except Exception:
        return []
