"""Unit tests for RST rendering utilities."""

from __future__ import annotations

from typing import Union

from sphinxcontrib.pydantic._rendering import (
    format_default_value,
    format_type_annotation,
)


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

    def test_formats_literal_type(self) -> None:
        """Test formatting of Literal types."""
        from typing import Literal

        result = format_type_annotation(Literal["a", "b", "c"])
        # Sphinx smart mode may add module prefix with ~
        assert "Literal" in result
        assert "'a'" in result
        assert "'b'" in result
        assert "'c'" in result

    def test_formats_callable_type(self) -> None:
        """Test formatting of Callable types."""
        from collections.abc import Callable

        result = format_type_annotation(Callable[[int, str], bool])
        assert "Callable" in result
        assert "int" in result
        assert "str" in result
        assert "bool" in result

    def test_formats_annotated_type(self) -> None:
        """Test formatting of Annotated types."""
        from typing import Annotated

        from pydantic import Field

        result = format_type_annotation(Annotated[int, Field(gt=0)])
        # Annotated types should show the base type
        assert "int" in result

    def test_formats_tuple_type(self) -> None:
        """Test formatting of tuple types."""
        result = format_type_annotation(tuple[int, str, float])
        assert result == "tuple[int, str, float]"

    def test_formats_tuple_ellipsis(self) -> None:
        """Test formatting of variable-length tuple."""
        result = format_type_annotation(tuple[int, ...])
        assert result == "tuple[int, ...]"


class TestFormatTypeAnnotationAsRst:
    """Tests for format_type_annotation with as_rst=True."""

    def test_formats_builtin_types_as_rst(self) -> None:
        """Test that builtin types become RST cross-references."""
        assert format_type_annotation(str, as_rst=True) == ":py:class:`str`"
        assert format_type_annotation(int, as_rst=True) == ":py:class:`int`"
        assert format_type_annotation(float, as_rst=True) == ":py:class:`float`"
        assert format_type_annotation(bool, as_rst=True) == ":py:class:`bool`"

    def test_formats_none_as_rst(self) -> None:
        """Test that None becomes RST py:obj reference."""
        assert format_type_annotation(None, as_rst=True) == ":py:obj:`None`"

    def test_formats_none_type_as_rst(self) -> None:
        """Test that type(None) becomes RST reference."""
        result = format_type_annotation(type(None), as_rst=True)
        assert ":py:obj:`None`" in result

    def test_formats_optional_type_as_rst(self) -> None:
        """Test that Optional types become RST with cross-references."""
        from typing import Optional

        result = format_type_annotation(Optional[str], as_rst=True)  # noqa: UP045
        assert ":py:class:`str`" in result
        assert ":py:obj:`None`" in result
        assert "|" in result  # Union separator

    def test_formats_union_type_as_rst(self) -> None:
        """Test that Union types become RST with cross-references."""
        result = format_type_annotation(Union[str, int], as_rst=True)  # noqa: UP007
        assert ":py:class:`str`" in result
        assert ":py:class:`int`" in result
        assert "|" in result  # Union separator

    def test_formats_list_type_as_rst(self) -> None:
        """Test that list types become RST with cross-references."""
        result = format_type_annotation(list[str], as_rst=True)
        assert ":py:class:`list`" in result
        assert ":py:class:`str`" in result

    def test_formats_dict_type_as_rst(self) -> None:
        """Test that dict types become RST with cross-references."""
        result = format_type_annotation(dict[str, int], as_rst=True)
        assert ":py:class:`dict`" in result
        assert ":py:class:`str`" in result
        assert ":py:class:`int`" in result

    def test_formats_nested_types_as_rst(self) -> None:
        """Test that nested generic types become RST with cross-references."""
        result = format_type_annotation(list[dict[str, int]], as_rst=True)
        assert ":py:class:`list`" in result
        assert ":py:class:`dict`" in result
        assert ":py:class:`str`" in result
        assert ":py:class:`int`" in result

    def test_formats_pathlib_path_as_rst(self) -> None:
        """Test that pathlib.Path becomes RST cross-reference with module."""
        from pathlib import Path

        result = format_type_annotation(Path, as_rst=True)
        assert ":py:class:`~pathlib.Path`" in result

    def test_formats_optional_path_as_rst(self) -> None:
        """Test that Optional[Path] becomes RST with cross-references."""
        from pathlib import Path
        from typing import Optional

        result = format_type_annotation(Optional[Path], as_rst=True)  # noqa: UP045
        assert ":py:class:`~pathlib.Path`" in result
        assert ":py:obj:`None`" in result

    def test_as_rst_false_returns_plain_text(self) -> None:
        """Test that as_rst=False (default) returns plain text."""
        # Default should be plain text
        assert format_type_annotation(str) == "str"
        assert format_type_annotation(str, as_rst=False) == "str"
        # Explicit as_rst=True should give RST
        assert format_type_annotation(str, as_rst=True) == ":py:class:`str`"


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
