"""Tests for the pydantic-model directive."""

from __future__ import annotations

from docutils.parsers.rst import directives

from sphinxcontrib.pydantic._directives._base import flag_or_value
from sphinxcontrib.pydantic._directives._model import PydanticModelDirective


class TestPydanticModelDirective:
    """Tests for the PydanticModelDirective class."""

    def test_inherits_from_base(self) -> None:
        """Directive inherits from PydanticDirective."""
        from sphinxcontrib.pydantic._directives._base import PydanticDirective

        assert issubclass(PydanticModelDirective, PydanticDirective)

    def test_has_model_specific_options(self) -> None:
        """Directive has model-specific options."""
        spec = PydanticModelDirective.option_spec
        assert "show-json" in spec
        assert "show-field-summary" in spec
        assert "show-validator-summary" in spec
        assert "show-config" in spec

    def test_options_use_flag_or_value(self) -> None:
        """Model-specific options use flag_or_value converter."""
        spec = PydanticModelDirective.option_spec
        assert spec["show-json"] == flag_or_value
        assert spec["show-field-summary"] == flag_or_value
        assert spec["show-validator-summary"] == flag_or_value
        assert spec["show-config"] == flag_or_value

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


class TestAutoPydanticModelDirective:
    """Tests for the AutoPydanticModelDirective class."""

    def test_exists(self) -> None:
        """AutoPydanticModelDirective exists."""
        from sphinxcontrib.pydantic._directives._model import (
            AutoPydanticModelDirective,
        )

        assert AutoPydanticModelDirective is not None

    def test_inherits_from_model_directive(self) -> None:
        """AutoPydanticModelDirective inherits from PydanticModelDirective."""
        from sphinxcontrib.pydantic._directives._model import (
            AutoPydanticModelDirective,
        )

        assert issubclass(AutoPydanticModelDirective, PydanticModelDirective)
