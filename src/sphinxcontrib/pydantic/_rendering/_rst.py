"""RST generation utilities for Pydantic documentation."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any


def format_type_annotation(annotation: Any) -> str:
    """Format a type annotation for display.

    Parameters
    ----------
    annotation : Any
        The type annotation to format.

    Returns
    -------
    str
        The formatted type annotation string.
    """
    if annotation is None:
        return "None"

    # Handle None type
    if annotation is type(None):
        return "None"

    # Handle basic types
    if isinstance(annotation, type):
        return annotation.__name__

    # Handle string annotations (forward references)
    if isinstance(annotation, str):
        return annotation

    # Handle typing module types
    origin = getattr(annotation, "__origin__", None)
    args = getattr(annotation, "__args__", None)

    if origin is not None:
        origin_name = getattr(origin, "__name__", str(origin))

        # Handle Union types (including Optional)
        if origin_name == "Union" or str(origin) == "typing.Union":
            if args:
                # Check if it's Optional (Union with None)
                if len(args) == 2 and type(None) in args:
                    non_none = [a for a in args if a is not type(None)][0]
                    return f"{format_type_annotation(non_none)} | None"
                return " | ".join(format_type_annotation(a) for a in args)

        # Handle other generic types
        if args:
            formatted_args = ", ".join(format_type_annotation(a) for a in args)
            return f"{origin_name}[{formatted_args}]"
        return origin_name

    # Fallback to string representation
    return str(annotation)


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

    if isinstance(value, str):
        return repr(value)

    if isinstance(value, bool):
        return str(value)

    if isinstance(value, (int, float)):
        return str(value)

    if isinstance(value, (list, tuple, dict, set)):
        return repr(value)

    # For other objects, use repr
    return repr(value)
