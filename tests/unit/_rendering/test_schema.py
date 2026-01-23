"""Tests for JSON schema RST rendering utilities."""

from __future__ import annotations

from sphinxcontrib.pydantic._rendering._schema import (
    format_schema_property,
    generate_json_schema_block,
)
from tests.assets.models.basic import DocumentedModel, SimpleModel


class TestGenerateJsonSchemaBlock:
    """Tests for generate_json_schema_block function."""

    def test_returns_list_of_strings(self) -> None:
        """Test that the function returns a list of strings."""
        result = generate_json_schema_block(SimpleModel)
        assert isinstance(result, list)
        assert all(isinstance(line, str) for line in result)

    def test_includes_title(self) -> None:
        """Test that the default title is included."""
        result = generate_json_schema_block(SimpleModel)
        assert any("JSON Schema" in line for line in result)

    def test_custom_title(self) -> None:
        """Test that a custom title can be provided."""
        result = generate_json_schema_block(SimpleModel, title="Custom Title")
        assert any("Custom Title" in line for line in result)

    def test_includes_code_block_directive(self) -> None:
        """Test that a code-block directive is included."""
        result = generate_json_schema_block(SimpleModel)
        assert any(".. code-block:: json" in line for line in result)

    def test_includes_json_content(self) -> None:
        """Test that JSON content is included."""
        result = generate_json_schema_block(SimpleModel)
        # Should contain property names from the model
        content = "\n".join(result)
        assert "name" in content
        assert "count" in content

    def test_collapsed_option(self) -> None:
        """Test that collapsed option wraps in collapse directive."""
        result = generate_json_schema_block(SimpleModel, collapsed=True)
        assert any(".. collapse::" in line for line in result)

    def test_not_collapsed_by_default(self) -> None:
        """Test that output is not collapsed by default."""
        result = generate_json_schema_block(SimpleModel)
        assert not any(".. collapse::" in line for line in result)

    def test_proper_indentation(self) -> None:
        """Test that JSON content is properly indented."""
        result = generate_json_schema_block(SimpleModel, collapsed=False)
        # After code-block directive, content should be indented
        in_code_block = False
        for line in result:
            if ".. code-block::" in line:
                in_code_block = True
                continue
            if in_code_block and line.strip():
                # Non-empty lines after code-block should be indented
                assert line.startswith("   "), f"Line not indented: {line!r}"


class TestFormatSchemaProperty:
    """Tests for format_schema_property function."""

    def test_returns_list_of_strings(self) -> None:
        """Test that the function returns a list of strings."""
        result = format_schema_property("name", {"type": "string"})
        assert isinstance(result, list)
        assert all(isinstance(line, str) for line in result)

    def test_includes_property_name(self) -> None:
        """Test that the property name is included."""
        result = format_schema_property("my_field", {"type": "string"})
        assert any("my_field" in line for line in result)

    def test_includes_type(self) -> None:
        """Test that the property type is included."""
        result = format_schema_property("name", {"type": "string"})
        content = "\n".join(result)
        assert "string" in content

    def test_includes_description(self) -> None:
        """Test that description is included when present."""
        result = format_schema_property(
            "name",
            {"type": "string", "description": "The name field"},
        )
        content = "\n".join(result)
        assert "The name field" in content

    def test_no_description_option(self) -> None:
        """Test that description can be hidden."""
        result = format_schema_property(
            "name",
            {"type": "string", "description": "The name field"},
            show_description=False,
        )
        content = "\n".join(result)
        assert "The name field" not in content

    def test_handles_ref(self) -> None:
        """Test that $ref is handled correctly."""
        result = format_schema_property(
            "address",
            {"$ref": "#/$defs/Address"},
        )
        content = "\n".join(result)
        assert "Address" in content

    def test_handles_anyof(self) -> None:
        """Test that anyOf is handled correctly."""
        result = format_schema_property(
            "value",
            {"anyOf": [{"type": "string"}, {"type": "integer"}]},
        )
        content = "\n".join(result)
        assert "string" in content or "integer" in content
