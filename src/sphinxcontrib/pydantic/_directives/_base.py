"""Base classes for Pydantic documentation directives."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from docutils.parsers.rst import directives
from sphinx.util.docutils import SphinxDirective

if TYPE_CHECKING:
    from typing import Any


def flag_or_value(argument: str | None) -> bool:
    """Convert a directive option that can be a flag or a boolean value.

    This allows options like ``:show-json:`` (flag style) or
    ``:show-json: true`` (explicit value style).

    Parameters
    ----------
    argument : str | None
        The argument value. None or empty string means flag was used.

    Returns
    -------
    bool
        True if flag was used or value is truthy, False otherwise.

    Raises
    ------
    ValueError
        If the argument is not a valid boolean string.
    """
    if argument is None or argument == "":
        return True

    lower = argument.lower()
    if lower in ("true", "yes", "1"):
        return True
    if lower in ("false", "no", "0"):
        return False

    raise ValueError(f"invalid boolean value: {argument!r}")


class PydanticDirective(SphinxDirective):
    """Base directive for documenting Pydantic objects.

    This provides common functionality for all Pydantic-related directives
    including model, field, validator, and settings directives.

    Subclasses should override ``run()`` to implement their specific behavior.
    """

    has_content: ClassVar[bool] = True
    required_arguments: ClassVar[int] = 1
    optional_arguments: ClassVar[int] = 0
    final_argument_whitespace: ClassVar[bool] = True

    option_spec: ClassVar[dict[str, Any]] = {
        "module": directives.unchanged,
        "noindex": directives.flag,
    }

    def get_object_path(self) -> str:
        """Get the full object path from arguments and options.

        Returns
        -------
        str
            The fully qualified object path (e.g., 'mymodule.MyModel').
        """
        name = self.arguments[0].strip()

        # If module option is provided, prepend it
        module = self.options.get("module")
        if module:
            return f"{module}.{name}"

        return name

    def get_config_value(self, name: str, default: Any = None) -> Any:
        """Get a configuration value from the Sphinx config.

        Parameters
        ----------
        name : str
            The configuration option name (without prefix).
        default : Any
            Default value if the configuration is not set.

        Returns
        -------
        Any
            The configuration value.
        """
        full_name = f"sphinxcontrib_pydantic_{name}"
        return getattr(self.config, full_name, default)

    def get_option_or_config(
        self,
        option_name: str,
        config_name: str,
        default: Any = None,
    ) -> Any:
        """Get a value from directive options, falling back to config.

        Parameters
        ----------
        option_name : str
            The directive option name.
        config_name : str
            The configuration name (without prefix).
        default : Any
            Default value if neither option nor config is set.

        Returns
        -------
        Any
            The value from options, config, or default.
        """
        if option_name in self.options:
            return self.options[option_name]

        return self.get_config_value(config_name, default)
