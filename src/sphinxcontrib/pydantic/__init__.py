"""Sphinx extension for documenting Pydantic models.

This extension provides enhanced documentation for Pydantic v2 models,
including automatic field and validator documentation.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sphinx.util import logging

from sphinxcontrib.pydantic._config import register_config
from sphinxcontrib.pydantic._directives import register_directives
from sphinxcontrib.pydantic._version import __version__

if TYPE_CHECKING:
    from typing import Any

    from sphinx.application import Sphinx

_logger = logging.getLogger(__name__)


def setup(app: Sphinx) -> dict[str, Any]:
    """Set up the sphinxcontrib-pydantic extension.

    This function is called by Sphinx when the extension is loaded.

    Parameters
    ----------
    app : Sphinx
        The Sphinx application instance.

    Returns
    -------
    dict[str, Any]
        Extension metadata including version and parallel safety flags.
    """
    _logger.debug("Initializing sphinxcontrib-pydantic extension")

    # Register configuration options
    register_config(app)

    # Register directives
    register_directives(app)

    # Register event handlers (will be implemented in Phase 4)
    # _register_events(app)

    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
