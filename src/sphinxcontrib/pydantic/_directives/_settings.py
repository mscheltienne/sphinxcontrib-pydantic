"""Pydantic settings documentation directive."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from docutils import nodes
from docutils.parsers.rst import directives
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

    def get_option_or_config(
        self,
        option_name: str,
        config_name: str,
        default: Any,
    ) -> Any:
        """Get an option value from directive options or Sphinx configuration.

        For settings directives, this looks up settings-specific config options
        first, falling back to model config options if not found.

        Parameters
        ----------
        option_name : str
            The directive option name (e.g., "show-json").
        config_name : str
            The Sphinx config name suffix (e.g., "model_show_json").
        default : Any
            Default value if not found in options or config.

        Returns
        -------
        Any
            The option value.
        """
        # First check directive options
        if option_name in self.options:
            value = self.options[option_name]
            # Handle flag options (None means True)
            if value is None:
                return True
            # Handle no-* options
            if option_name.startswith("no-"):
                return False
            return value

        # Check for settings-specific config first
        settings_config_name = config_name.replace("model_", "settings_")
        full_settings_config = f"sphinxcontrib_pydantic_{settings_config_name}"

        if hasattr(self.state.document.settings.env.config, full_settings_config):
            return getattr(
                self.state.document.settings.env.config, full_settings_config
            )

        # Fall back to model config
        full_config = f"sphinxcontrib_pydantic_{config_name}"
        if hasattr(self.state.document.settings.env.config, full_config):
            return getattr(self.state.document.settings.env.config, full_config)

        return default


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
