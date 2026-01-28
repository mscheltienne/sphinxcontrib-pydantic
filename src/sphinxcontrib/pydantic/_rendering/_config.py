"""Configuration for RST generation.

This module provides a centralized configuration system for model documentation
generation. The `GeneratorConfig` dataclass holds all configuration values,
and factory functions create instances from either Sphinx config or directive
options.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from sphinx.application import Sphinx


@dataclass(frozen=True, slots=True)
class GeneratorConfig:
    """Configuration for model documentation generation.

    This dataclass has NO default values. All values must be provided
    by the factory functions (config_from_sphinx or config_from_directive).
    This ensures failures are explicit rather than hidden by defaults.

    Attributes
    ----------
    show_field_summary : bool
        Whether to show the field summary table.
    show_validator_summary : bool
        Whether to show the validator summary table.
    show_json : bool
        Whether to show the JSON schema.
    field_show_alias : bool
        Whether to show field aliases in the summary table.
    field_show_default : bool
        Whether to show default values in the summary table.
    field_show_required : bool
        Whether to show required/optional indicators.
    field_show_constraints : bool
        Whether to show field constraints.
    validator_list_fields : bool
        Whether to list fields in the validator summary.
    signature_prefix : str
        Prefix for the model signature (e.g., "model" or "settings").
    hide_paramlist : bool
        Whether to hide the parameter list in signatures.
    """

    # Summary options
    show_field_summary: bool
    show_validator_summary: bool
    show_json: bool

    # Field display options
    field_show_alias: bool
    field_show_default: bool
    field_show_required: bool
    field_show_constraints: bool

    # Validator display options
    validator_list_fields: bool

    # Signature options
    signature_prefix: str
    hide_paramlist: bool


def config_from_sphinx(app: Sphinx, prefix: str = "model") -> GeneratorConfig:
    """Create GeneratorConfig from Sphinx application config.

    Parameters
    ----------
    app : Sphinx
        The Sphinx application.
    prefix : str
        Config prefix: "model" or "settings".

    Returns
    -------
    GeneratorConfig
        Configuration populated from Sphinx config values.
    """

    def get(name: str, default: Any) -> Any:
        full_name = f"sphinxcontrib_pydantic_{prefix}_{name}"
        return getattr(app.config, full_name, default)

    def get_field(name: str, default: Any) -> Any:
        full_name = f"sphinxcontrib_pydantic_field_{name}"
        return getattr(app.config, full_name, default)

    def get_validator(name: str, default: Any) -> Any:
        full_name = f"sphinxcontrib_pydantic_validator_{name}"
        return getattr(app.config, full_name, default)

    return GeneratorConfig(
        show_field_summary=get("show_field_summary", True),
        show_validator_summary=get("show_validator_summary", True),
        show_json=get("show_json", False),
        field_show_alias=get_field("show_alias", True),
        field_show_default=get_field("show_default", True),
        field_show_required=get_field("show_required", True),
        field_show_constraints=get_field("show_constraints", True),
        validator_list_fields=get_validator("list_fields", True),
        signature_prefix=get("signature_prefix", prefix),
        hide_paramlist=get("hide_paramlist", True),
    )


def config_from_directive(
    options: dict[str, Any],
    sphinx_config: Any,
    prefix: str = "model",
) -> GeneratorConfig:
    """Create GeneratorConfig from directive options with Sphinx config fallback.

    Parameters
    ----------
    options : dict[str, Any]
        Directive options.
    sphinx_config : Any
        Sphinx config object.
    prefix : str
        Config prefix: "model" or "settings".

    Returns
    -------
    GeneratorConfig
        Configuration populated from options with config fallback.
    """

    def get(option_name: str, config_suffix: str, default: Any) -> Any:
        # Check directive option first
        if option_name in options:
            value = options[option_name]
            # Handle flag options (None means True)
            return True if value is None else value
        # Fall back to Sphinx config
        full_name = f"sphinxcontrib_pydantic_{prefix}_{config_suffix}"
        return getattr(sphinx_config, full_name, default)

    def get_field(option_name: str, config_suffix: str, default: Any) -> Any:
        if option_name in options:
            value = options[option_name]
            return True if value is None else value
        full_name = f"sphinxcontrib_pydantic_field_{config_suffix}"
        return getattr(sphinx_config, full_name, default)

    def get_validator(option_name: str, config_suffix: str, default: Any) -> Any:
        if option_name in options:
            value = options[option_name]
            return True if value is None else value
        full_name = f"sphinxcontrib_pydantic_validator_{config_suffix}"
        return getattr(sphinx_config, full_name, default)

    return GeneratorConfig(
        show_field_summary=get("show-field-summary", "show_field_summary", True),
        show_validator_summary=get(
            "show-validator-summary", "show_validator_summary", True
        ),
        show_json=get("show-json", "show_json", False),
        field_show_alias=get_field("show-alias", "show_alias", True),
        field_show_default=get_field("show-default", "show_default", True),
        field_show_required=get_field("show-required", "show_required", True),
        field_show_constraints=get_field("show-constraints", "show_constraints", True),
        validator_list_fields=get_validator("list-fields", "list_fields", True),
        signature_prefix=get("signature-prefix", "signature_prefix", prefix),
        hide_paramlist=get("hide-paramlist", "hide_paramlist", True),
    )
