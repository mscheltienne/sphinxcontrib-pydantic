"""Unit tests for RST rendering utilities."""

from __future__ import annotations

from typing import Union

from sphinxcontrib.pydantic._rendering import (
    escape_rst,
    format_default_value,
    format_field_signature,
    format_type_annotation,
    indent,
)


class TestIndent:
    """Tests for indent function."""

    def test_indents_lines_with_default_prefix(self) -> None:
        """Test that lines are indented with default prefix."""
        lines = ["line1", "line2"]
        result = indent(lines)
        assert result == ["   line1", "   line2"]

    def test_indents_lines_with_custom_prefix(self) -> None:
        """Test that lines are indented with custom prefix."""
        lines = ["line1", "line2"]
        result = indent(lines, prefix=">>> ")
        assert result == [">>> line1", ">>> line2"]

    def test_preserves_empty_lines(self) -> None:
        """Test that empty lines are preserved without indentation."""
        lines = ["line1", "", "line2"]
        result = indent(lines)
        assert result == ["   line1", "", "   line2"]

    def test_preserves_whitespace_only_lines(self) -> None:
        """Test that whitespace-only lines are not additionally indented."""
        lines = ["line1", "   ", "line2"]
        result = indent(lines)
        assert result == ["   line1", "   ", "   line2"]


class TestFormatTypeAnnotation:
    """Tests for format_type_annotation function."""

    def test_formats_builtin_types(self) -> None:
        """Test formatting of builtin types."""
        assert format_type_annotation(str) == "str"
        assert format_type_annotation(int) == "int"
        assert format_type_annotation(float) == "float"
        assert format_type_annotation(bool) == "bool"

    def test_formats_none_type(self) -> None:
        """Test formatting of None type."""
        assert format_type_annotation(None) == "None"
        assert format_type_annotation(type(None)) == "None"

    def test_formats_optional_type(self) -> None:
        """Test formatting of Optional types."""
        from typing import Optional

        # Need to use typing.Optional to test the function handles legacy syntax
        result = format_type_annotation(Optional[str])  # noqa: UP045
        assert result == "str | None"

    def test_formats_union_type(self) -> None:
        """Test formatting of Union types."""
        # Need to use typing.Union to test the function handles legacy syntax
        result = format_type_annotation(Union[str, int])  # noqa: UP007
        assert result == "str | int"

    def test_formats_list_type(self) -> None:
        """Test formatting of List types."""
        result = format_type_annotation(list[str])
        assert result == "list[str]"

    def test_formats_dict_type(self) -> None:
        """Test formatting of Dict types."""
        result = format_type_annotation(dict[str, int])
        assert result == "dict[str, int]"

    def test_formats_nested_types(self) -> None:
        """Test formatting of nested generic types."""
        result = format_type_annotation(list[dict[str, int]])
        assert result == "list[dict[str, int]]"

    def test_formats_string_annotations(self) -> None:
        """Test formatting of string annotations (forward references)."""
        assert format_type_annotation("MyClass") == "MyClass"


class TestFormatDefaultValue:
    """Tests for format_default_value function."""

    def test_formats_none(self) -> None:
        """Test formatting of None."""
        assert format_default_value(None) == "None"

    def test_formats_strings(self) -> None:
        """Test formatting of strings."""
        assert format_default_value("hello") == "'hello'"

    def test_formats_integers(self) -> None:
        """Test formatting of integers."""
        assert format_default_value(42) == "42"
        assert format_default_value(0) == "0"
        assert format_default_value(-1) == "-1"

    def test_formats_floats(self) -> None:
        """Test formatting of floats."""
        assert format_default_value(3.14) == "3.14"

    def test_formats_booleans(self) -> None:
        """Test formatting of booleans."""
        assert format_default_value(True) == "True"
        assert format_default_value(False) == "False"

    def test_formats_lists(self) -> None:
        """Test formatting of lists."""
        assert format_default_value([1, 2, 3]) == "[1, 2, 3]"
        assert format_default_value([]) == "[]"

    def test_formats_dicts(self) -> None:
        """Test formatting of dicts."""
        assert format_default_value({"a": 1}) == "{'a': 1}"
        assert format_default_value({}) == "{}"


class TestEscapeRst:
    """Tests for escape_rst function."""

    def test_escapes_asterisks(self) -> None:
        """Test escaping of asterisks."""
        assert escape_rst("*bold*") == "\\*bold\\*"

    def test_escapes_backticks(self) -> None:
        """Test escaping of backticks."""
        assert escape_rst("`code`") == "\\`code\\`"

    def test_escapes_backslashes(self) -> None:
        """Test escaping of backslashes."""
        assert escape_rst("path\\to\\file") == "path\\\\to\\\\file"

    def test_preserves_normal_text(self) -> None:
        """Test that normal text is preserved."""
        assert escape_rst("hello world") == "hello world"


class TestFormatFieldSignature:
    """Tests for format_field_signature function."""

    def test_formats_simple_signature(self) -> None:
        """Test formatting of simple field signature."""
        result = format_field_signature("name", str)
        assert result == "name: str"

    def test_formats_signature_with_alias(self) -> None:
        """Test formatting of signature with alias."""
        result = format_field_signature("name", str, alias="external_name")
        assert result == "name: str (alias: 'external_name')"

    def test_hides_alias_when_show_alias_false(self) -> None:
        """Test that alias is hidden when show_alias is False."""
        result = format_field_signature(
            "name", str, alias="external_name", show_alias=False
        )
        assert result == "name: str"

    def test_formats_complex_type(self) -> None:
        """Test formatting with complex type."""
        result = format_field_signature("items", list[str])
        assert result == "items: list[str]"
