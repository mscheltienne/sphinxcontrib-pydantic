"""Unit tests for cross-reference utilities."""

from __future__ import annotations

from sphinxcontrib.pydantic._rendering import create_role_reference


class TestCreateRoleReference:
    """Tests for create_role_reference function."""

    def test_default_role(self) -> None:
        """Test that default role is py:obj."""
        result = create_role_reference("name", "module.Class.name")

        assert result == ":py:obj:`name <module.Class.name>`"

    def test_custom_role(self) -> None:
        """Test with custom role."""
        result = create_role_reference("MyClass", "module.MyClass", role="py:class")

        assert result == ":py:class:`MyClass <module.MyClass>`"

    def test_method_role(self) -> None:
        """Test with method role."""
        result = create_role_reference("method", "module.Class.method", role="py:meth")

        assert result == ":py:meth:`method <module.Class.method>`"

    def test_attribute_role(self) -> None:
        """Test with attribute role."""
        result = create_role_reference("attr", "module.Class.attr", role="py:attr")

        assert result == ":py:attr:`attr <module.Class.attr>`"

    def test_handles_complex_paths(self) -> None:
        """Test with complex module paths."""
        result = create_role_reference(
            "field",
            "package.subpackage.module.Class.field",
        )

        assert result == ":py:obj:`field <package.subpackage.module.Class.field>`"

    def test_handles_special_characters_in_name(self) -> None:
        """Test with underscores in name."""
        result = create_role_reference(
            "_private_field",
            "module.Class._private_field",
        )

        assert result == ":py:obj:`_private_field <module.Class._private_field>`"
