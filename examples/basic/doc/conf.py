"""Sphinx configuration for example-basic."""

from __future__ import annotations

project = "example-basic"
author = "sphinxcontrib-pydantic"
copyright = "2025, sphinxcontrib-pydantic"  # noqa: A001
release = "0.1.0"

# Extensions
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
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

# Autodoc
autodoc_member_order = "bysource"

# sphinxcontrib-pydantic
sphinxcontrib_pydantic_model_show_field_summary = True
sphinxcontrib_pydantic_model_show_validator_summary = True
sphinxcontrib_pydantic_field_show_alias = True
sphinxcontrib_pydantic_field_show_constraints = True

# Intersphinx
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "pydantic": ("https://docs.pydantic.dev/latest/", None),
}
