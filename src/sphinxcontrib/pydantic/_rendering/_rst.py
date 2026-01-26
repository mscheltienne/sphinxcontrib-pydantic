"""RST generation utilities for Pydantic documentation."""

from __future__ import annotations

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
