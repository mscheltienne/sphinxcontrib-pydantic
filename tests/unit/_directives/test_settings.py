"""Tests for pydantic-settings directive."""

from __future__ import annotations

from sphinxcontrib.pydantic._directives._base import PydanticDirective
from sphinxcontrib.pydantic._directives._model import PydanticModelDirective
from sphinxcontrib.pydantic._directives._settings import (
    AutoPydanticSettingsDirective,
    PydanticSettingsDirective,
)


class TestPydanticSettingsDirective:
    """Tests for PydanticSettingsDirective class."""

    def test_inherits_from_model_directive(self) -> None:
        """Test that PydanticSettingsDirective inherits from PydanticModelDirective."""
        assert issubclass(PydanticSettingsDirective, PydanticModelDirective)

    def test_inherits_from_base(self) -> None:
        """Test that PydanticSettingsDirective inherits from PydanticDirective."""
        assert issubclass(PydanticSettingsDirective, PydanticDirective)

    def test_has_option_spec(self) -> None:
        """Test that directive has option_spec."""
        assert hasattr(PydanticSettingsDirective, "option_spec")
        assert isinstance(PydanticSettingsDirective.option_spec, dict)

    def test_inherits_model_options(self) -> None:
        """Test that settings directive inherits model options."""
        model_options = set(PydanticModelDirective.option_spec.keys())
        settings_options = set(PydanticSettingsDirective.option_spec.keys())
        # Settings should have at least all model options
        assert model_options.issubset(settings_options)

    def test_has_show_json_option(self) -> None:
        """Test that directive has show-json option."""
        assert "show-json" in PydanticSettingsDirective.option_spec

    def test_has_show_field_summary_option(self) -> None:
        """Test that directive has show-field-summary option."""
        assert "show-field-summary" in PydanticSettingsDirective.option_spec

    def test_has_show_validator_summary_option(self) -> None:
        """Test that directive has show-validator-summary option."""
        assert "show-validator-summary" in PydanticSettingsDirective.option_spec

    def test_has_members_option(self) -> None:
        """Test that directive has members option."""
        assert "members" in PydanticSettingsDirective.option_spec


class TestAutoPydanticSettingsDirective:
    """Tests for AutoPydanticSettingsDirective class."""

    def test_exists(self) -> None:
        """Test that AutoPydanticSettingsDirective exists."""
        assert AutoPydanticSettingsDirective is not None

    def test_inherits_from_settings_directive(self) -> None:
        """Test that AutoPydanticSettingsDirective inherits from settings."""
        assert issubclass(AutoPydanticSettingsDirective, PydanticSettingsDirective)
