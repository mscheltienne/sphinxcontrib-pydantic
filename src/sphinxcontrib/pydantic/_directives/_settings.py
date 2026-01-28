"""Pydantic settings documentation directive."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from docutils import nodes
from sphinx.util import logging

from sphinxcontrib.pydantic._directives._model import PydanticModelDirective
from sphinxcontrib.pydantic._inspection import is_pydantic_settings

if TYPE_CHECKING:
    from typing import Any

    from sphinx.application import Sphinx

_logger = logging.getLogger(__name__)


class PydanticSettingsDirective(PydanticModelDirective):
    """Directive for documenting a Pydantic settings model.

    Usage::

        .. pydantic-settings:: mymodule.MySettings
           :show-json:
           :show-field-summary:
           :show-validator-summary:

    Or with explicit module::

        .. pydantic-settings:: MySettings
           :module: mymodule
    """

    #: Config prefix for looking up Sphinx config values
    _config_prefix: ClassVar[str] = "settings"

    option_spec: ClassVar[dict[str, Any]] = {
        **PydanticModelDirective.option_spec,
    }

    def run(self) -> list[nodes.Node]:
        """Run the directive and generate documentation nodes.

        Returns
        -------
        list[nodes.Node]
            List of docutils nodes representing the settings documentation.
        """
        # Get the settings class
        objpath = self.get_object_path()
        model = self._import_model(objpath)

        if model is None:
            return [
                self.state.document.reporter.warning(
                    f"Cannot find Pydantic settings: {objpath}",
                    line=self.lineno,
                )
            ]

        if not is_pydantic_settings(model):
            return [
                self.state.document.reporter.warning(
                    f"Object is not a Pydantic settings class: {objpath}",
                    line=self.lineno,
                )
            ]

        # Get model info (settings are also models)
        from sphinxcontrib.pydantic._inspection import get_model_info

        model_info = get_model_info(model)

        # Generate the documentation using parent's method
        return self._generate_model_docs(model, model_info)


class AutoPydanticSettingsDirective(PydanticSettingsDirective):
    """Auto-documenting directive for Pydantic settings.

    This directive automatically imports and documents a Pydantic settings class,
    similar to autodoc's ``autoclass`` directive.

    Usage::

        .. autopydantic-settings:: mymodule.MySettings
           :members:
           :show-field-summary:
    """


def register_settings_directives(app: Sphinx) -> None:
    """Register settings directives with Sphinx.

    Parameters
    ----------
    app : Sphinx
        The Sphinx application instance.
    """
    app.add_directive("pydantic-settings", PydanticSettingsDirective)
    app.add_directive("autopydantic-settings", AutoPydanticSettingsDirective)
