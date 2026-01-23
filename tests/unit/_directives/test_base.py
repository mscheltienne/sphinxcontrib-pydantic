"""Tests for the base directive classes."""

from __future__ import annotations

import pytest
from docutils.parsers.rst import directives

from sphinxcontrib.pydantic._directives._base import (
    PydanticDirective,
    flag_or_value,
)


class TestFlagOrValue:
    """Tests for the flag_or_value option converter."""

    def test_returns_true_for_none(self) -> None:
        """When no value is given (flag style), returns True."""
        assert flag_or_value(None) is True

    def test_returns_true_for_empty_string(self) -> None:
        """When empty string is given, returns True."""
        assert flag_or_value("") is True

    def test_returns_true_for_true_string(self) -> None:
        """When 'true' string is given, returns True."""
        assert flag_or_value("true") is True
        assert flag_or_value("True") is True
        assert flag_or_value("TRUE") is True

    def test_returns_false_for_false_string(self) -> None:
        """When 'false' string is given, returns False."""
        assert flag_or_value("false") is False
        assert flag_or_value("False") is False
        assert flag_or_value("FALSE") is False

    def test_returns_true_for_yes(self) -> None:
        """When 'yes' string is given, returns True."""
        assert flag_or_value("yes") is True

    def test_returns_false_for_no(self) -> None:
        """When 'no' string is given, returns False."""
        assert flag_or_value("no") is False

    def test_raises_for_invalid_value(self) -> None:
        """Invalid values raise ValueError."""
        with pytest.raises(ValueError, match="invalid boolean"):
            flag_or_value("invalid")


class TestPydanticDirective:
    """Tests for the PydanticDirective base class."""

    def test_has_required_class_attributes(self) -> None:
        """Directive has required class attributes."""
        assert hasattr(PydanticDirective, "has_content")
        assert hasattr(PydanticDirective, "required_arguments")
        assert hasattr(PydanticDirective, "optional_arguments")
        assert hasattr(PydanticDirective, "option_spec")

    def test_required_arguments_is_one(self) -> None:
        """Directive requires one argument (the object path)."""
        assert PydanticDirective.required_arguments == 1

    def test_has_content_is_true(self) -> None:
        """Directive can have content."""
        assert PydanticDirective.has_content is True

    def test_option_spec_includes_module(self) -> None:
        """Option spec includes module option."""
        assert "module" in PydanticDirective.option_spec
        assert PydanticDirective.option_spec["module"] == directives.unchanged

    def test_option_spec_includes_noindex(self) -> None:
        """Option spec includes noindex flag."""
        assert "noindex" in PydanticDirective.option_spec
        assert PydanticDirective.option_spec["noindex"] == directives.flag
