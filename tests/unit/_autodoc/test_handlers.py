"""Tests for autodoc event handlers."""

from __future__ import annotations

from sphinxcontrib.pydantic._autodoc._handlers import (
    PYDANTIC_SKIP_MEMBERS,
    is_pydantic_internal,
    should_skip_member,
)
from tests.assets.models.basic import SimpleModel
from tests.assets.models.validators import SingleFieldValidator


class TestIsPydanticInternal:
    """Tests for is_pydantic_internal function."""

    def test_model_fields_is_internal(self) -> None:
        """Test that model_fields is detected as internal."""
        assert is_pydantic_internal("model_fields") is True

    def test_model_config_is_internal(self) -> None:
        """Test that model_config is detected as internal."""
        assert is_pydantic_internal("model_config") is True

    def test_model_computed_fields_is_internal(self) -> None:
        """Test that model_computed_fields is detected as internal."""
        assert is_pydantic_internal("model_computed_fields") is True

    def test_regular_field_not_internal(self) -> None:
        """Test that regular fields are not internal."""
        assert is_pydantic_internal("name") is False
        assert is_pydantic_internal("value") is False

    def test_dunder_methods_not_internal(self) -> None:
        """Test that dunder methods are not flagged as pydantic internal."""
        # Dunder methods should be handled separately by autodoc
        assert is_pydantic_internal("__init__") is False

    def test_pydantic_private_attrs_internal(self) -> None:
        """Test that __pydantic prefixed attrs are internal."""
        assert is_pydantic_internal("__pydantic_decorators__") is True
        assert is_pydantic_internal("__pydantic_fields_set__") is True


class TestShouldSkipMember:
    """Tests for should_skip_member function."""

    def test_skips_model_fields(self) -> None:
        """Test that model_fields attribute is skipped."""
        result = should_skip_member(
            what="attribute",
            name="model_fields",
            obj=SimpleModel.model_fields,
            skip=False,
            options={},
        )
        assert result is True

    def test_skips_model_config(self) -> None:
        """Test that model_config attribute is skipped."""
        result = should_skip_member(
            what="attribute",
            name="model_config",
            obj=SimpleModel.model_config,
            skip=False,
            options={},
        )
        assert result is True

    def test_does_not_skip_regular_attributes(self) -> None:
        """Test that regular attributes are not skipped."""
        result = should_skip_member(
            what="attribute",
            name="some_attr",
            obj="value",
            skip=False,
            options={},
        )
        assert result is None  # None means don't change skip decision

    def test_respects_existing_skip_true(self) -> None:
        """Test that existing skip=True is preserved."""
        result = should_skip_member(
            what="attribute",
            name="some_attr",
            obj="value",
            skip=True,
            options={},
        )
        assert result is None  # Don't override existing skip decision

    def test_does_not_skip_methods(self) -> None:
        """Test that methods are not skipped by our handler."""
        result = should_skip_member(
            what="method",
            name="model_dump",
            obj=SimpleModel.model_dump,
            skip=False,
            options={},
        )
        # We only skip attributes, not methods
        assert result is None


class TestPydanticSkipMembers:
    """Tests for the PYDANTIC_SKIP_MEMBERS constant."""

    def test_contains_model_fields(self) -> None:
        """Test that model_fields is in skip list."""
        assert "model_fields" in PYDANTIC_SKIP_MEMBERS

    def test_contains_model_config(self) -> None:
        """Test that model_config is in skip list."""
        assert "model_config" in PYDANTIC_SKIP_MEMBERS

    def test_contains_model_computed_fields(self) -> None:
        """Test that model_computed_fields is in skip list."""
        assert "model_computed_fields" in PYDANTIC_SKIP_MEMBERS

    def test_contains_pydantic_complete(self) -> None:
        """Test that __pydantic_complete__ is in skip list."""
        assert "__pydantic_complete__" in PYDANTIC_SKIP_MEMBERS
