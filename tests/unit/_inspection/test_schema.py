"""Tests for JSON schema inspection utilities."""

from __future__ import annotations

import pytest

from sphinxcontrib.pydantic._inspection._schema import (
    SchemaInfo,
    generate_json_schema,
    get_schema_info,
)
from tests.assets.models.basic import DocumentedModel, SimpleModel
from tests.assets.models.fields import FieldWithConstraints, FieldWithDefaults
from tests.assets.models.nested import Address, Person


class TestGetSchemaInfo:
    """Tests for get_schema_info function."""

    def test_returns_schema_info(self) -> None:
        """Test that get_schema_info returns a SchemaInfo object."""
        result = get_schema_info(SimpleModel)
        assert isinstance(result, SchemaInfo)

    def test_schema_contains_title(self) -> None:
        """Test that schema info contains model title."""
        result = get_schema_info(SimpleModel)
        assert result.title == "SimpleModel"

    def test_schema_contains_properties(self) -> None:
        """Test that schema info contains field properties."""
        result = get_schema_info(SimpleModel)
        assert "name" in result.properties
        assert "count" in result.properties

    def test_schema_contains_required_fields(self) -> None:
        """Test that required fields are identified."""
        result = get_schema_info(FieldWithDefaults)
        assert "required_field" in result.required
        assert "default_value" not in result.required

    def test_schema_contains_description(self) -> None:
        """Test that model description is captured."""
        result = get_schema_info(DocumentedModel)
        assert result.description is not None
        assert "documented fields" in result.description.lower()

    def test_nested_model_has_definitions(self) -> None:
        """Test that nested models create definitions."""
        result = get_schema_info(Person)
        # Person has an Address field, so it should have definitions
        assert "Address" in result.definitions or len(result.definitions) > 0


class TestGenerateJsonSchema:
    """Tests for generate_json_schema function."""

    def test_returns_string(self) -> None:
        """Test that generate_json_schema returns a string."""
        result = generate_json_schema(SimpleModel)
        assert isinstance(result, str)

    def test_returns_valid_json(self) -> None:
        """Test that the returned string is valid JSON."""
        import json

        result = generate_json_schema(SimpleModel)
        schema = json.loads(result)
        assert isinstance(schema, dict)

    def test_respects_indent_option(self) -> None:
        """Test that indent option is respected."""
        result_2 = generate_json_schema(SimpleModel, indent=2)
        result_4 = generate_json_schema(SimpleModel, indent=4)
        # More indentation means longer string (same content, more spaces)
        assert len(result_4) > len(result_2)

    def test_sort_keys_option(self) -> None:
        """Test that sort_keys option is respected."""
        import json

        result = generate_json_schema(SimpleModel, sort_keys=True)
        schema = json.loads(result)
        # Check that properties are sorted (if there are any)
        if "properties" in schema:
            props = list(schema["properties"].keys())
            assert props == sorted(props)

    def test_includes_constraints(self) -> None:
        """Test that field constraints are included in schema."""
        import json

        result = generate_json_schema(FieldWithConstraints)
        schema = json.loads(result)

        # Check for constraint metadata
        props = schema.get("properties", {})
        if "bounded" in props:
            bounded = props["bounded"]
            # Should have minimum and maximum
            assert "minimum" in bounded or "exclusiveMinimum" in bounded
            assert "maximum" in bounded or "exclusiveMaximum" in bounded


class TestSchemaInfoDataclass:
    """Tests for SchemaInfo dataclass."""

    def test_is_frozen(self) -> None:
        """Test that SchemaInfo is immutable."""
        info = get_schema_info(SimpleModel)
        with pytest.raises(AttributeError):
            info.title = "NewTitle"  # type: ignore[misc]

    def test_has_slots(self) -> None:
        """Test that SchemaInfo uses slots."""
        info = get_schema_info(SimpleModel)
        assert hasattr(info, "__slots__") or not hasattr(info, "__dict__")
