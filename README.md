[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![codecov](https://codecov.io/gh/mscheltienne/sphinxcontrib-pydantic/graph/badge.svg?token=AC0qhhaeVW)](https://codecov.io/gh/mscheltienne/sphinxcontrib-pydantic)
[![tests](https://github.com/mscheltienne/sphinxcontrib-pydantic/actions/workflows/pytest.yaml/badge.svg?branch=main)](https://github.com/mscheltienne/sphinxcontrib-pydantic/actions/workflows/pytest.yaml)
[![examples](https://github.com/mscheltienne/sphinxcontrib-pydantic/actions/workflows/examples.yaml/badge.svg?branch=main)](https://github.com/mscheltienne/sphinxcontrib-pydantic/actions/workflows/examples.yaml)

# sphinxcontrib-pydantic

A Sphinx extension for documenting Pydantic models in your documentation.

This project was inspired by [autodoc_pydantic](https://github.com/mansenfranzen/autodoc_pydantic),
which I have been using for years but has gone unmaintained and is now incompatible
with **Sphinx 9.0+**. Unlike its predecessor, `sphinxcontrib-pydantic` focuses
exclusively on modern versions: **Pydantic v2+** and **Sphinx 9.0+** (Python 3.11+).

This project was vibe-coded using Claude Code (Opus 4.5); using `autodoc_pydantic` as
inspiration as well as the source code of `sphinx` and `pydantic` as documentation.

## Installation

```bash
pip install sphinxcontrib-pydantic
```

For `pydantic-settings` support:

```bash
pip install sphinxcontrib-pydantic[settings]
```

## Configuration

Enable the extension in your `conf.py`:

```python
extensions = [
    "sphinx.ext.autodoc",
    "sphinxcontrib.pydantic",
]
```

## Usage

### With autodoc

The extension integrates with `sphinx.ext.autodoc`. Simply use `automodule` or
`autoclass`:

```rst
.. automodule:: mypackage.models
   :members:
```

Pydantic models are automatically detected and documented with field summaries and
validators.

### With autosummary

For larger projects, use `autosummary` with a custom template:

```rst
.. currentmodule:: mypackage.models

.. autosummary::
   :toctree: generated/api
   :template: autosummary/models.rst

   UserConfig
   DatabaseConfig
```

Create `_templates/autosummary/models.rst`:

```jinja
{{ fullname | escape | underline }}

.. currentmodule:: {{ module }}

.. pydantic-model:: {{ fullname }}
   :inherited-members: BaseModel
```

### Standalone directives

Document models directly with the `pydantic-model` directive:

```rst
.. pydantic-model:: mypackage.models.UserConfig
   :show-field-summary:
   :show-validator-summary:
```

For Pydantic settings:

```rst
.. pydantic-settings:: mypackage.settings.AppSettings
   :show-field-summary:
```

## Configuration Options

All options use the `sphinxcontrib_pydantic_` prefix in `conf.py`, e.g.
`sphinxcontrib_pydantic_model_show_json`.

### Model Options

| Option | Default | Description |
|--------|---------|-------------|
| `sphinxcontrib_pydantic_model_show_json` | `False` | Show JSON schema for the model |
| `sphinxcontrib_pydantic_model_show_field_summary` | `True` | Show summary table of fields |
| `sphinxcontrib_pydantic_model_show_validator_summary` | `True` | Show summary table of validators |
| `sphinxcontrib_pydantic_model_show_config` | `False` | Show model configuration |
| `sphinxcontrib_pydantic_model_signature_prefix` | `"model"` | Prefix shown before model name |
| `sphinxcontrib_pydantic_model_hide_paramlist` | `True` | Hide `__init__` parameter list |

### Field Options

| Option | Default | Description |
|--------|---------|-------------|
| `sphinxcontrib_pydantic_field_show_alias` | `True` | Show field aliases |
| `sphinxcontrib_pydantic_field_show_default` | `True` | Show default values |
| `sphinxcontrib_pydantic_field_show_required` | `True` | Show required status |
| `sphinxcontrib_pydantic_field_show_constraints` | `True` | Show field constraints (e.g., `min_length`) |

### Validator Options

| Option | Default | Description |
|--------|---------|-------------|
| `sphinxcontrib_pydantic_validator_list_fields` | `True` | List fields affected by each validator |

### Settings Options

Settings options mirror model options with `settings_` prefix (e.g.,
`sphinxcontrib_pydantic_settings_show_json`). They default to the same values as their
model counterparts.

| Option | Default | Description |
|--------|---------|-------------|
| `sphinxcontrib_pydantic_settings_show_json` | `False` | Show JSON schema for the setting |
| `sphinxcontrib_pydantic_settings_show_field_summary` | `True` | Show summary table of fields |
| `sphinxcontrib_pydantic_settings_show_validator_summary` | `True` | Show summary table of validators |
| `sphinxcontrib_pydantic_settings_show_config` | `False` | Show setting configuration |
| `sphinxcontrib_pydantic_settings_signature_prefix` | `"model"` | Prefix shown before setting name |
| `sphinxcontrib_pydantic_settings_hide_paramlist` | `True` | Hide `__init__` parameter list |

### Example Configuration

```python
# conf.py
sphinxcontrib_pydantic_model_show_json = True
sphinxcontrib_pydantic_model_show_field_summary = True
sphinxcontrib_pydantic_field_show_constraints = True
sphinxcontrib_pydantic_settings_signature_prefix = "config"
```
