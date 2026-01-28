"""Tests for the pydantic-model directive."""

from __future__ import annotations

from docutils.parsers.rst import directives

from sphinxcontrib.pydantic._directives import (
    AutoPydanticModelDirective,
    PydanticDirective,
    PydanticModelDirective,
    flag_or_value,
)


class TestPydanticModelDirective:
    """Tests for the PydanticModelDirective class."""

    def test_inherits_from_base(self) -> None:
        """Directive inherits from PydanticDirective."""
        assert issubclass(PydanticModelDirective, PydanticDirective)

    def test_has_model_specific_options(self) -> None:
        """Directive has model-specific options."""
        spec = PydanticModelDirective.option_spec
        assert "show-json" in spec
        assert "show-field-summary" in spec
        assert "show-validator-summary" in spec

    def test_options_use_flag_or_value(self) -> None:
        """Model-specific options use flag_or_value converter."""
        spec = PydanticModelDirective.option_spec
        assert spec["show-json"] == flag_or_value
        assert spec["show-field-summary"] == flag_or_value
        assert spec["show-validator-summary"] == flag_or_value

    def test_has_members_option(self) -> None:
        """Directive has members option for autodoc-like behavior."""
        spec = PydanticModelDirective.option_spec
        assert "members" in spec
        assert spec["members"] == directives.unchanged

    def test_has_inherited_members_option(self) -> None:
        """Directive has inherited-members option."""
        spec = PydanticModelDirective.option_spec
        assert "inherited-members" in spec
        # Uses unchanged to accept exclude list like autodoc's inherited-members
        assert spec["inherited-members"] == directives.unchanged

    def test_has_undoc_members_option(self) -> None:
        """Directive has undoc-members option."""
        spec = PydanticModelDirective.option_spec
        assert "undoc-members" in spec
        assert spec["undoc-members"] == directives.flag

    def test_has_field_display_options(self) -> None:
        """Directive has field display options for per-directive override."""
        spec = PydanticModelDirective.option_spec
        assert "show-alias" in spec
        assert "show-default" in spec
        assert "show-required" in spec
        assert "show-constraints" in spec

    def test_has_validator_display_options(self) -> None:
        """Directive has validator display options."""
        spec = PydanticModelDirective.option_spec
        assert "list-fields" in spec

    def test_has_signature_options(self) -> None:
        """Directive has signature customization options."""
        spec = PydanticModelDirective.option_spec
        assert "signature-prefix" in spec
        assert "hide-paramlist" in spec

    def test_field_options_use_flag_or_value(self) -> None:
        """Field display options use flag_or_value converter."""
        spec = PydanticModelDirective.option_spec
        assert spec["show-alias"] == flag_or_value
        assert spec["show-default"] == flag_or_value
        assert spec["show-required"] == flag_or_value
        assert spec["show-constraints"] == flag_or_value

    def test_validator_options_use_flag_or_value(self) -> None:
        """Validator display options use flag_or_value converter."""
        spec = PydanticModelDirective.option_spec
        assert spec["list-fields"] == flag_or_value

    def test_signature_prefix_uses_unchanged(self) -> None:
        """signature-prefix accepts string values."""
        spec = PydanticModelDirective.option_spec
        assert spec["signature-prefix"] == directives.unchanged

    def test_hide_paramlist_uses_flag_or_value(self) -> None:
        """hide-paramlist option uses flag_or_value converter."""
        spec = PydanticModelDirective.option_spec
        assert spec["hide-paramlist"] == flag_or_value


class TestAutoPydanticModelDirective:
    """Tests for the AutoPydanticModelDirective class."""

    def test_exists(self) -> None:
        """AutoPydanticModelDirective exists."""
        assert AutoPydanticModelDirective is not None

    def test_inherits_from_model_directive(self) -> None:
        """AutoPydanticModelDirective inherits from PydanticModelDirective."""
        assert issubclass(AutoPydanticModelDirective, PydanticModelDirective)
