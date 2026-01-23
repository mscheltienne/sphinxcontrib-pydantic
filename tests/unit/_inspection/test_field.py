"""Unit tests for field inspection."""

from __future__ import annotations

import pytest

from sphinxcontrib.pydantic._inspection import FieldInfo, get_field_info


class TestGetFieldInfo:
    """Tests for get_field_info function."""

    def test_returns_field_info(self) -> None:
        """Test that FieldInfo is returned for a model field."""
        from tests.assets.models.basic import SimpleModel

        info = get_field_info(SimpleModel, "name")

        assert isinstance(info, FieldInfo)
        assert info.name == "name"

    def test_extracts_type_annotation(self) -> None:
        """Test that type annotation is extracted."""
        from tests.assets.models.basic import SimpleModel

        info = get_field_info(SimpleModel, "name")

        assert info.annotation == str

    def test_extracts_default_value(self) -> None:
        """Test that default value is extracted."""
        from tests.assets.models.basic import SimpleModel

        info = get_field_info(SimpleModel, "count")

        assert info.default == 0
        assert info.has_default is True

    def test_required_field_has_no_default(self) -> None:
        """Test that required fields have no default."""
        from tests.assets.models.basic import SimpleModel

        info = get_field_info(SimpleModel, "name")

        assert info.has_default is False
        assert info.is_required is True

    def test_optional_field_not_required(self) -> None:
        """Test that optional fields are not required."""
        from tests.assets.models.fields import FieldWithDefaults

        info = get_field_info(FieldWithDefaults, "optional_field")

        assert info.is_required is False

    def test_raises_for_invalid_field(self) -> None:
        """Test that KeyError is raised for non-existent fields."""
        from tests.assets.models.basic import SimpleModel

        with pytest.raises(KeyError, match="not_a_field"):
            get_field_info(SimpleModel, "not_a_field")

    def test_raises_for_non_pydantic_model(self) -> None:
        """Test that TypeError is raised for non-Pydantic models."""

        class NotAModel:
            pass

        with pytest.raises(TypeError, match="not a Pydantic model"):
            get_field_info(NotAModel, "field")


class TestFieldInfoAlias:
    """Tests for field alias extraction."""

    def test_extracts_alias(self) -> None:
        """Test that field alias is extracted."""
        from tests.assets.models.fields import FieldWithAlias

        info = get_field_info(FieldWithAlias, "internal_name")

        assert info.alias == "externalName"

    def test_no_alias_returns_none(self) -> None:
        """Test that fields without alias return None."""
        from tests.assets.models.basic import SimpleModel

        info = get_field_info(SimpleModel, "name")

        assert info.alias is None


class TestFieldInfoDescription:
    """Tests for field description extraction."""

    def test_extracts_description(self) -> None:
        """Test that field description is extracted."""
        from tests.assets.models.basic import DocumentedModel

        info = get_field_info(DocumentedModel, "name")

        assert info.description == "The name of the item."

    def test_no_description_returns_none(self) -> None:
        """Test that fields without description return None."""
        from tests.assets.models.basic import SimpleModel

        info = get_field_info(SimpleModel, "name")

        assert info.description is None


class TestFieldInfoConstraints:
    """Tests for field constraint extraction."""

    def test_extracts_ge_constraint(self) -> None:
        """Test that ge constraint is extracted."""
        from tests.assets.models.fields import FieldWithConstraints

        info = get_field_info(FieldWithConstraints, "bounded")

        assert info.constraints.get("ge") == 0

    def test_extracts_le_constraint(self) -> None:
        """Test that le constraint is extracted."""
        from tests.assets.models.fields import FieldWithConstraints

        info = get_field_info(FieldWithConstraints, "bounded")

        assert info.constraints.get("le") == 100

    def test_extracts_min_length_constraint(self) -> None:
        """Test that min_length constraint is extracted."""
        from tests.assets.models.fields import FieldWithConstraints

        info = get_field_info(FieldWithConstraints, "length_bounded")

        assert info.constraints.get("min_length") == 1

    def test_extracts_max_length_constraint(self) -> None:
        """Test that max_length constraint is extracted."""
        from tests.assets.models.fields import FieldWithConstraints

        info = get_field_info(FieldWithConstraints, "length_bounded")

        assert info.constraints.get("max_length") == 50

    def test_extracts_pattern_constraint(self) -> None:
        """Test that pattern constraint is extracted."""
        from tests.assets.models.fields import FieldWithConstraints

        info = get_field_info(FieldWithConstraints, "pattern_field")

        assert info.constraints.get("pattern") == r"^[a-z]+$"

    def test_no_constraints_returns_empty_dict(self) -> None:
        """Test that fields without constraints return empty dict."""
        from tests.assets.models.basic import SimpleModel

        info = get_field_info(SimpleModel, "name")

        assert info.constraints == {}


class TestFieldInfoDefaultFactory:
    """Tests for field default_factory extraction."""

    def test_extracts_default_factory(self) -> None:
        """Test that default_factory is detected."""
        from tests.assets.models.fields import FieldWithDefaults

        info = get_field_info(FieldWithDefaults, "factory_default")

        assert info.has_default_factory is True

    def test_no_default_factory_returns_false(self) -> None:
        """Test that fields without default_factory return False."""
        from tests.assets.models.basic import SimpleModel

        info = get_field_info(SimpleModel, "count")

        assert info.has_default_factory is False


class TestFieldInfo:
    """Tests for FieldInfo dataclass."""

    def test_has_required_attributes(self) -> None:
        """Test that FieldInfo has all required attributes."""
        from tests.assets.models.basic import SimpleModel

        info = get_field_info(SimpleModel, "name")

        # Basic attributes
        assert hasattr(info, "name")
        assert hasattr(info, "annotation")
        assert hasattr(info, "default")
        assert hasattr(info, "has_default")
        assert hasattr(info, "has_default_factory")
        assert hasattr(info, "is_required")

        # Metadata
        assert hasattr(info, "alias")
        assert hasattr(info, "description")
        assert hasattr(info, "constraints")
        assert hasattr(info, "title")
        assert hasattr(info, "examples")
