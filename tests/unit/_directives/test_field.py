"""Tests for the pydantic-field directive."""

from __future__ import annotations

from docutils.parsers.rst import directives

from sphinxcontrib.pydantic._directives._base import flag_or_value
from sphinxcontrib.pydantic._directives._field import PydanticFieldDirective


class TestPydanticFieldDirective:
    """Tests for the PydanticFieldDirective class."""

    def test_inherits_from_base(self) -> None:
        """Directive inherits from PydanticDirective."""
        from sphinxcontrib.pydantic._directives._base import PydanticDirective

        assert issubclass(PydanticFieldDirective, PydanticDirective)

    def test_has_model_option(self) -> None:
        """Directive has model option to specify parent model."""
        spec = PydanticFieldDirective.option_spec
        assert "model" in spec
        assert spec["model"] == directives.unchanged_required

    def test_has_field_specific_options(self) -> None:
        """Directive has field-specific options."""
        spec = PydanticFieldDirective.option_spec
        assert "show-alias" in spec
        assert "show-default" in spec
        assert "show-constraints" in spec

    def test_options_use_flag_or_value(self) -> None:
        """Field-specific options use flag_or_value converter."""
        spec = PydanticFieldDirective.option_spec
        assert spec["show-alias"] == flag_or_value
        assert spec["show-default"] == flag_or_value
        assert spec["show-constraints"] == flag_or_value
