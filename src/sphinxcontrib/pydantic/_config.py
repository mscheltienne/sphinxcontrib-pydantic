"""Configuration options for sphinxcontrib-pydantic.

This module defines all configuration options that can be set in conf.py.
All options use the ``sphinxcontrib_pydantic_`` prefix.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sphinx.application import Sphinx

# Configuration option definitions: (name, default, rebuild_type)
# rebuild_type: 'html' = rebuild HTML, 'env' = rebuild entire environment
_CONFIG_OPTIONS: list[tuple[str, object, str]] = [
    # Model options
    ("sphinxcontrib_pydantic_model_show_json", False, "html"),
    ("sphinxcontrib_pydantic_model_show_field_summary", True, "html"),
    ("sphinxcontrib_pydantic_model_show_validator_summary", True, "html"),
    ("sphinxcontrib_pydantic_model_show_config", False, "html"),
    ("sphinxcontrib_pydantic_model_signature_prefix", "model", "html"),
    ("sphinxcontrib_pydantic_model_hide_paramlist", True, "html"),
    # Field options
    ("sphinxcontrib_pydantic_field_show_alias", True, "html"),
    ("sphinxcontrib_pydantic_field_show_default", True, "html"),
    ("sphinxcontrib_pydantic_field_show_required", True, "html"),
    ("sphinxcontrib_pydantic_field_show_constraints", True, "html"),
    # Validator options
    ("sphinxcontrib_pydantic_validator_list_fields", True, "html"),
    # Settings options (inherit from model options by default)
    ("sphinxcontrib_pydantic_settings_show_json", False, "html"),
    ("sphinxcontrib_pydantic_settings_show_field_summary", True, "html"),
    ("sphinxcontrib_pydantic_settings_show_validator_summary", True, "html"),
    ("sphinxcontrib_pydantic_settings_show_config", False, "html"),
    ("sphinxcontrib_pydantic_settings_signature_prefix", "settings", "html"),
    ("sphinxcontrib_pydantic_settings_hide_paramlist", True, "html"),
]


def register_config(app: Sphinx) -> None:
    """Register all configuration options with Sphinx.

    Parameters
    ----------
    app : Sphinx
        The Sphinx application instance.
    """
    for name, default, rebuild in _CONFIG_OPTIONS:
        app.add_config_value(name, default, rebuild)
