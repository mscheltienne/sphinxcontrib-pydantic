"""Tests for configuration utilities."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock

import pytest

from sphinxcontrib.pydantic._rendering._config import (
    GeneratorConfig,
    config_from_directive,
    config_from_sphinx,
)

if TYPE_CHECKING:
    from typing import Any


class TestGeneratorConfig:
    """Tests for GeneratorConfig dataclass."""

    def test_all_fields_required(self) -> None:
        """Test that all fields must be provided."""
        # Verify that missing arguments raises TypeError
        with pytest.raises(TypeError):
            GeneratorConfig()

    def test_frozen_immutable(self) -> None:
        """Test that config is immutable."""
        config = GeneratorConfig(
            show_field_summary=True,
            show_validator_summary=True,
            show_json=False,
            show_members=True,
            field_show_alias=True,
            field_show_default=True,
            field_show_required=True,
            field_show_constraints=True,
            validator_list_fields=True,
            signature_prefix="model",
            hide_paramlist=True,
        )
        with pytest.raises(AttributeError):
            config.show_field_summary = False

    def test_all_fields_populated(self) -> None:
        """Test that all fields are accessible."""
        config = GeneratorConfig(
            show_field_summary=True,
            show_validator_summary=False,
            show_json=True,
            show_members=False,
            field_show_alias=True,
            field_show_default=False,
            field_show_required=True,
            field_show_constraints=False,
            validator_list_fields=True,
            signature_prefix="settings",
            hide_paramlist=False,
        )

        assert config.show_field_summary is True
        assert config.show_validator_summary is False
        assert config.show_json is True
        assert config.show_members is False
        assert config.field_show_alias is True
        assert config.field_show_default is False
        assert config.field_show_required is True
        assert config.field_show_constraints is False
        assert config.validator_list_fields is True
        assert config.signature_prefix == "settings"
        assert config.hide_paramlist is False


class TestConfigFromSphinx:
    """Tests for config_from_sphinx factory function."""

    def _make_app(self, **config_values: Any) -> MagicMock:
        """Create a mock Sphinx app with config values.

        Uses a custom object for config that only has the specified attributes,
        allowing getattr with default to work properly.
        """
        app = MagicMock()

        # Create a simple namespace object that only has specified attributes
        class ConfigNamespace:
            pass

        config = ConfigNamespace()
        for name, value in config_values.items():
            setattr(config, name, value)

        app.config = config
        return app

    def test_uses_model_prefix_by_default(self) -> None:
        """Test that model prefix is used by default."""
        app = self._make_app(
            sphinxcontrib_pydantic_model_show_field_summary=False,
        )
        config = config_from_sphinx(app)
        assert config.show_field_summary is False

    def test_uses_settings_prefix_when_specified(self) -> None:
        """Test that settings prefix is used when specified."""
        app = self._make_app(
            sphinxcontrib_pydantic_settings_show_field_summary=False,
            sphinxcontrib_pydantic_model_show_field_summary=True,
        )
        config = config_from_sphinx(app, prefix="settings")
        assert config.show_field_summary is False

    def test_uses_default_when_not_configured(self) -> None:
        """Test that defaults are used for unconfigured options."""
        # Create app with empty config (getattr returns default)
        app = self._make_app()

        config = config_from_sphinx(app)

        # Check defaults - these will be the hardcoded defaults in the function
        assert config.show_field_summary is True
        assert config.show_validator_summary is True
        assert config.show_json is False
        assert config.show_members is True
        assert config.field_show_alias is True
        assert config.field_show_default is True
        assert config.field_show_required is True
        assert config.field_show_constraints is True
        assert config.validator_list_fields is True
        assert config.hide_paramlist is True

    def test_signature_prefix_defaults_to_prefix(self) -> None:
        """Test that signature_prefix defaults to the config prefix."""
        app = self._make_app()
        config = config_from_sphinx(app, prefix="model")
        assert config.signature_prefix == "model"

        config = config_from_sphinx(app, prefix="settings")
        assert config.signature_prefix == "settings"

    def test_field_config_uses_field_prefix(self) -> None:
        """Test that field options use field_ prefix."""
        app = self._make_app(
            sphinxcontrib_pydantic_field_show_alias=False,
            sphinxcontrib_pydantic_field_show_default=False,
        )
        config = config_from_sphinx(app)
        assert config.field_show_alias is False
        assert config.field_show_default is False

    def test_validator_config_uses_validator_prefix(self) -> None:
        """Test that validator options use validator_ prefix."""
        app = self._make_app(
            sphinxcontrib_pydantic_validator_list_fields=False,
        )
        config = config_from_sphinx(app)
        assert config.validator_list_fields is False


class TestConfigFromDirective:
    """Tests for config_from_directive factory function."""

    def _make_config(self, **values: Any) -> MagicMock:
        """Create a mock Sphinx config."""
        config = MagicMock(spec=[])
        for name, value in values.items():
            setattr(config, name, value)
        return config

    def test_directive_option_overrides_config(self) -> None:
        """Test that directive options override Sphinx config."""
        sphinx_config = self._make_config(
            sphinxcontrib_pydantic_model_show_field_summary=True,
        )
        options = {"show-field-summary": False}

        config = config_from_directive(options, sphinx_config)
        assert config.show_field_summary is False

    def test_falls_back_to_sphinx_config(self) -> None:
        """Test that Sphinx config is used when option not present."""
        sphinx_config = self._make_config(
            sphinxcontrib_pydantic_model_show_field_summary=False,
        )
        options: dict[str, Any] = {}

        config = config_from_directive(options, sphinx_config)
        assert config.show_field_summary is False

    def test_flag_option_treated_as_true(self) -> None:
        """Test that flag options (None value) are treated as True."""
        sphinx_config = self._make_config()
        # Flag options have None value
        options = {"show-json": None}

        config = config_from_directive(options, sphinx_config)
        assert config.show_json is True

    def test_field_options_override_config(self) -> None:
        """Test that field-related directive options work."""
        sphinx_config = self._make_config(
            sphinxcontrib_pydantic_field_show_alias=True,
        )
        options = {"show-alias": False}

        config = config_from_directive(options, sphinx_config)
        assert config.field_show_alias is False

    def test_validator_options_override_config(self) -> None:
        """Test that validator-related directive options work."""
        sphinx_config = self._make_config(
            sphinxcontrib_pydantic_validator_list_fields=True,
        )
        options = {"list-fields": False}

        config = config_from_directive(options, sphinx_config)
        assert config.validator_list_fields is False

    def test_uses_settings_prefix(self) -> None:
        """Test that settings prefix is used when specified."""
        sphinx_config = self._make_config(
            sphinxcontrib_pydantic_settings_show_json=True,
            sphinxcontrib_pydantic_model_show_json=False,
        )
        options: dict[str, Any] = {}

        config = config_from_directive(options, sphinx_config, prefix="settings")
        assert config.show_json is True

    def test_uses_default_when_not_configured(self) -> None:
        """Test that defaults are used when neither option nor config present."""
        sphinx_config = self._make_config()
        options: dict[str, Any] = {}

        config = config_from_directive(options, sphinx_config)
        assert config.show_field_summary is True  # default
        assert config.show_json is False  # default

    def test_signature_prefix_from_directive(self) -> None:
        """Test that signature-prefix option works."""
        sphinx_config = self._make_config()
        options = {"signature-prefix": "pydantic model"}

        config = config_from_directive(options, sphinx_config)
        assert config.signature_prefix == "pydantic model"

    def test_hide_paramlist_from_directive(self) -> None:
        """Test that hide-paramlist option works."""
        sphinx_config = self._make_config()
        options = {"hide-paramlist": False}

        config = config_from_directive(options, sphinx_config)
        assert config.hide_paramlist is False
