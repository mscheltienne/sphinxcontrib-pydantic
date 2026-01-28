"""Sphinx configuration for example-autosummary."""

from __future__ import annotations

from intersphinx_registry import get_intersphinx_mapping

project = "example-autosummary"
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
templates_path = ["_templates"]
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
autodoc_typehints = "none"
autodoc_warningiserror = True

# sphinxcontrib-pydantic
sphinxcontrib_pydantic_model_show_json = False
sphinxcontrib_pydantic_model_show_field_summary = True
sphinxcontrib_pydantic_model_show_validator_summary = True
sphinxcontrib_pydantic_field_show_alias = True
sphinxcontrib_pydantic_field_show_default = True
sphinxcontrib_pydantic_field_show_required = True
sphinxcontrib_pydantic_field_show_constraints = True

# numpydoc
numpydoc_class_members_toctree = False
numpydoc_attributes_as_param_list = False
numpydoc_xref_param_type = True

# Disable inherited class members for Pydantic models to avoid broken cross-references
numpydoc_show_inherited_class_members = {
    "example_autosummary.models.UserConfig": False,
    "example_autosummary.models.DatabaseConfig": False,
    "example_autosummary.models.AppConfig": False,
    "example_autosummary.database.dto.UserDTO": False,
    "example_autosummary.database.table.UserTable": False,
}

# Intersphinx
intersphinx_mapping = get_intersphinx_mapping(packages={"python", "sqlalchemy"})
intersphinx_mapping.update(
    {
        "pydantic": ("https://docs.pydantic.dev/latest/", None),
    }
)

# Nitpick ignore for types without intersphinx inventories
nitpick_ignore = [
    # SQLModel has no intersphinx inventory
    ("py:class", "sqlmodel.main.SQLModel"),
]

# Nitpick ignore regex for fields shown in summary tables but not documented
# (fields lack docstrings and numpydoc_show_inherited_class_members=False)
nitpick_ignore_regex = [
    # Fields in summary tables that aren't documented as attributes
    (r"py:obj", r"example_autosummary\.models\.\w+\.\w+"),
    (r"py:obj", r"example_autosummary\.database\.\w+\.\w+\.\w+"),
]
