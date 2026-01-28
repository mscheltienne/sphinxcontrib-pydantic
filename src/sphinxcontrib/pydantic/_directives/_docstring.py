"""Docstring processing utilities for Pydantic directives."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sphinx.util import logging

if TYPE_CHECKING:
    from sphinx.application import Sphinx

_logger = logging.getLogger(__name__)


def process_docstring(
    app: Sphinx,
    docstring: str,
    *,
    what: str = "class",
    name: str = "",
    obj: object | None = None,
) -> list[str]:
    """Process a docstring through registered autodoc handlers.

    Emits the ``autodoc-process-docstring`` event to allow extensions like
    Napoleon and numpydoc to process the docstring. If the event is not
    registered (autodoc not loaded), returns the raw docstring lines.

    Parameters
    ----------
    app : Sphinx
        The Sphinx application instance.
    docstring : str
        The raw docstring text.
    what : str
        Type of object being documented ('class', 'function', 'method', etc.).
    name : str
        Fully qualified name of the object.
    obj : object | None
        The actual Python object (used by some processors).

    Returns
    -------
    list[str]
        Processed docstring lines ready for nested_parse().
    """
    if not docstring:
        return []

    stripped = docstring.strip()
    if not stripped:
        return []

    lines = stripped.split("\n")

    # Check if the autodoc-process-docstring event is registered
    # This event is registered by autodoc, which Napoleon and numpydoc depend on
    if "autodoc-process-docstring" not in app.events.events:
        _logger.debug(
            "autodoc-process-docstring event not registered, "
            "returning raw docstring for %s",
            name,
        )
        return lines

    # Emit the event - handlers modify lines in-place
    # Parameters match what autodoc passes:
    # - what: object type ('module', 'class', 'function', 'method', 'attribute')
    # - name: fully qualified name
    # - obj: the actual Python object
    # - options: autodoc options (None is valid - handlers check for it)
    # - lines: docstring lines (modified in-place by handlers)
    app.emit(
        "autodoc-process-docstring",
        what,
        name,
        obj,
        None,  # options - Napoleon/numpydoc handle None gracefully
        lines,
    )

    return lines
