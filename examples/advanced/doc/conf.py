"""Sphinx configuration for example-advanced."""

from __future__ import annotations

from intersphinx_registry import get_intersphinx_mapping

project = "example-advanced"
author = "sphinxcontrib-pydantic"
copyright = "2025, sphinxcontrib-pydantic"  # noqa: A001
release = "0.1.0"

# Extensions
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "numpydoc",
    "sphinxcontrib.pydantic",
]

# General
root_doc = "index"
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
nitpicky = True
default_role = "py:obj"

# HTML
html_theme = "furo"
html_title = project
html_show_sphinx = False
html_theme_options = {
    "footer_icons": [],
}

# Autodoc / autosummary
autosummary_generate = True
autodoc_member_order = "groupwise"
autoclass_content = "class"

# sphinxcontrib-pydantic (all options enabled for demonstration)
sphinxcontrib_pydantic_model_show_json = True
sphinxcontrib_pydantic_model_show_field_summary = True
sphinxcontrib_pydantic_model_show_validator_summary = True
sphinxcontrib_pydantic_model_show_config = True
sphinxcontrib_pydantic_field_show_alias = True
sphinxcontrib_pydantic_field_show_default = True
sphinxcontrib_pydantic_field_show_required = True
sphinxcontrib_pydantic_field_show_constraints = True
sphinxcontrib_pydantic_validator_list_fields = True

# Settings (same as model but with settings prefix)
sphinxcontrib_pydantic_settings_show_json = False
sphinxcontrib_pydantic_settings_show_field_summary = True

# numpydoc
numpydoc_class_members_toctree = False
numpydoc_attributes_as_param_list = False
numpydoc_xref_param_type = True

# Intersphinx
intersphinx_mapping = get_intersphinx_mapping(packages={"python"})
intersphinx_mapping.update(
    {
        "pydantic": ("https://docs.pydantic.dev/latest/", None),
    }
)
