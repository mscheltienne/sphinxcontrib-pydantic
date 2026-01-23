"""JSON schema RST rendering utilities."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any

    from pydantic import BaseModel


def generate_json_schema_block(
    model: type[BaseModel],
    *,
    title: str = "JSON Schema",
    collapsed: bool = False,
    indent: int = 2,
) -> list[str]:
    """Generate RST lines for a JSON schema code block.

    Parameters
    ----------
    model : type[BaseModel]
        The Pydantic model class.
    title : str, optional
        Title for the schema section, by default "JSON Schema".
    collapsed : bool, optional
        Whether to wrap in a collapsed section, by default False.
    indent : int, optional
        JSON indentation level, by default 2.

    Returns
    -------
    list[str]
        RST lines for the schema block.
    """
    import json

    try:
        schema = model.model_json_schema()
        schema_str = json.dumps(schema, indent=indent)
    except Exception:
        return []

    lines: list[str] = []

    if collapsed:
        lines.extend(
            [
                f".. collapse:: {title}",
                "",
                "   .. code-block:: json",
                "",
            ]
        )
        # Indent the schema for the collapse directive
        for line in schema_str.split("\n"):
            lines.append("      " + line if line else "")
    else:
        lines.extend(
            [
                f"**{title}**",
                "",
                ".. code-block:: json",
                "",
            ]
        )
        # Indent the schema for the code-block directive
        for line in schema_str.split("\n"):
            lines.append("   " + line if line else "")

    return lines


def format_schema_property(
    name: str,
    prop: dict[str, Any],
    *,
    show_description: bool = True,
) -> list[str]:
    """Format a single schema property for RST.

    Parameters
    ----------
    name : str
        The property name.
    prop : dict[str, Any]
        The property schema.
    show_description : bool, optional
        Whether to show the description, by default True.

    Returns
    -------
    list[str]
        RST lines describing the property.
    """
    lines: list[str] = []

    # Build type string
    prop_type = prop.get("type", "any")
    if "$ref" in prop:
        # Reference to another definition
        ref = prop["$ref"]
        if ref.startswith("#/$defs/"):
            prop_type = ref[8:]  # Remove "#/$defs/" prefix
        else:
            prop_type = ref

    # Handle anyOf/oneOf
    if "anyOf" in prop:
        types = []
        for item in prop["anyOf"]:
            if "type" in item:
                types.append(item["type"])
            elif "$ref" in item:
                ref = item["$ref"]
                if ref.startswith("#/$defs/"):
                    types.append(ref[8:])
        prop_type = " | ".join(types) if types else "any"

    lines.append(f"- **{name}** (*{prop_type}*)")

    if show_description and "description" in prop:
        lines.append(f"  {prop['description']}")

    return lines
