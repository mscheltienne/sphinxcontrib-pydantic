"""Tests for the pydantic-validator directive."""

from __future__ import annotations

from docutils.parsers.rst import directives

from sphinxcontrib.pydantic._directives._base import PydanticDirective, flag_or_value
from sphinxcontrib.pydantic._directives._validator import PydanticValidatorDirective


class TestPydanticValidatorDirective:
    """Tests for the PydanticValidatorDirective class."""

    def test_inherits_from_base(self) -> None:
        """Directive inherits from PydanticDirective."""
        assert issubclass(PydanticValidatorDirective, PydanticDirective)

    def test_has_model_option(self) -> None:
        """Directive has model option to specify parent model."""
        spec = PydanticValidatorDirective.option_spec
        assert "model" in spec
        assert spec["model"] == directives.unchanged_required

    def test_has_validator_specific_options(self) -> None:
        """Directive has validator-specific options."""
        spec = PydanticValidatorDirective.option_spec
        assert "list-fields" in spec

    def test_options_use_flag_or_value(self) -> None:
        """Validator-specific options use flag_or_value converter."""
        spec = PydanticValidatorDirective.option_spec
        assert spec["list-fields"] == flag_or_value
