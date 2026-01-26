"""Tests for the pydantic_field directive."""

from __future__ import annotations

from docutils.parsers.rst import directives
from sphinx.domains.python import PyAttribute

from sphinxcontrib.pydantic._directives._field import PydanticFieldDirective


class TestPydanticFieldDirective:
    """Tests for the PydanticFieldDirective class."""

    def test_inherits_from_py_attribute(self) -> None:
        """Directive inherits from PyAttribute."""
        assert issubclass(PydanticFieldDirective, PyAttribute)

    def test_has_required_option(self) -> None:
        """Directive has required flag option."""
        spec = PydanticFieldDirective.option_spec
        assert "required" in spec
        assert spec["required"] == directives.flag

    def test_has_optional_option(self) -> None:
        """Directive has optional flag option."""
        spec = PydanticFieldDirective.option_spec
        assert "optional" in spec
        assert spec["optional"] == directives.flag

    def test_inherits_py_attribute_options(self) -> None:
        """Directive inherits all PyAttribute options."""
        spec = PydanticFieldDirective.option_spec
        # PyAttribute options should be present
        assert "type" in spec
        assert "value" in spec
        assert "noindex" in spec

    def test_option_spec_is_copy_not_reference(self) -> None:
        """Directive option_spec is a copy, not a reference to parent."""
        # Ensure we didn't accidentally modify the parent class
        assert "required" not in PyAttribute.option_spec
        assert "optional" not in PyAttribute.option_spec
