"""Sphinx directives for Pydantic models."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sphinxcontrib.pydantic._directives._base import PydanticDirective, flag_or_value
from sphinxcontrib.pydantic._directives._field import PydanticFieldDirective
from sphinxcontrib.pydantic._directives._model import (
    AutoPydanticModelDirective,
    PydanticModelDirective,
)
from sphinxcontrib.pydantic._directives._model import (
    register_directives as _register_model_directives,
)
from sphinxcontrib.pydantic._directives._settings import (
    AutoPydanticSettingsDirective,
    PydanticSettingsDirective,
)
from sphinxcontrib.pydantic._directives._settings import (
    register_settings_directives as _register_settings_directives,
)

if TYPE_CHECKING:
    from sphinx.application import Sphinx


def register_directives(app: Sphinx) -> None:
    """Register all Pydantic directives with Sphinx.

    Parameters
    ----------
    app : Sphinx
        The Sphinx application instance.
    """
    _register_model_directives(app)
    _register_settings_directives(app)

    # Register pydantic_field directive in Python domain
    app.add_directive_to_domain("py", "pydantic_field", PydanticFieldDirective)
