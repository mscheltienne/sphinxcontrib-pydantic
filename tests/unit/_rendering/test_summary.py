"""Unit tests for summary table generation."""

from __future__ import annotations

from sphinxcontrib.pydantic._inspection import get_field_info, get_validator_info
from sphinxcontrib.pydantic._rendering import (
    create_role_reference,
    generate_field_summary_table,
    generate_root_type_line,
    generate_validator_summary_table,
)
from tests.assets.models.basic import SimpleModel
from tests.assets.models.fields import FieldWithAlias, FieldWithConstraints
from tests.assets.models.root_model import IntList, StringMapping
from tests.assets.models.validators import (
    BeforeValidator,
    ModelValidatorAfter,
    MultiFieldValidator,
    SingleFieldValidator,
)


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


class TestGenerateFieldSummaryTable:
    """Tests for generate_field_summary_table function."""

    def test_generates_table_for_simple_model(self) -> None:
        """Test that a table is generated for a simple model."""
        fields = [
            get_field_info(SimpleModel, "name"),
            get_field_info(SimpleModel, "count"),
        ]

        result = generate_field_summary_table(fields)

        # Check that result is a list of lines
        assert isinstance(result, list)
        assert len(result) > 0

        # Check for table directive
        table_content = "\n".join(result)
        assert ".. list-table:: Fields" in table_content
        assert ":header-rows: 1" in table_content

    def test_includes_field_names(self) -> None:
        """Test that field names are included in the table."""
        fields = [
            get_field_info(SimpleModel, "name"),
            get_field_info(SimpleModel, "count"),
        ]

        result = generate_field_summary_table(fields)
        table_content = "\n".join(result)

        assert "``name``" in table_content
        assert "``count``" in table_content

    def test_includes_field_types(self) -> None:
        """Test that field types are included in the table."""
        fields = [
            get_field_info(SimpleModel, "name"),
            get_field_info(SimpleModel, "count"),
        ]

        result = generate_field_summary_table(fields)
        table_content = "\n".join(result)

        assert "``str``" in table_content
        assert "``int``" in table_content

    def test_includes_required_indicator(self) -> None:
        """Test that required indicator is included."""
        fields = [
            get_field_info(SimpleModel, "name"),
            get_field_info(SimpleModel, "count"),
        ]

        result = generate_field_summary_table(fields, show_required=True)
        table_content = "\n".join(result)

        assert "Required" in table_content
        assert "Yes" in table_content  # name is required
        assert "No" in table_content  # count has default

    def test_includes_default_values(self) -> None:
        """Test that default values are included."""
        fields = [
            get_field_info(SimpleModel, "count"),
        ]

        result = generate_field_summary_table(fields, show_default=True)
        table_content = "\n".join(result)

        assert "``0``" in table_content

    def test_includes_aliases(self) -> None:
        """Test that aliases are included when present."""
        fields = [
            get_field_info(FieldWithAlias, "internal_name"),
        ]

        result = generate_field_summary_table(fields, show_alias=True)
        table_content = "\n".join(result)

        assert "Alias" in table_content
        assert "``externalName``" in table_content

    def test_includes_constraints(self) -> None:
        """Test that constraints are included when present."""
        fields = [
            get_field_info(FieldWithConstraints, "bounded"),
        ]

        result = generate_field_summary_table(fields, show_constraints=True)
        table_content = "\n".join(result)

        assert "Constraints" in table_content
        assert "ge=0" in table_content
        assert "le=100" in table_content

    def test_returns_empty_for_no_fields(self) -> None:
        """Test that empty list is returned for no fields."""
        result = generate_field_summary_table([])
        assert result == []

    def test_hides_alias_column_when_no_aliases(self) -> None:
        """Test that alias column is hidden when no fields have aliases."""
        fields = [
            get_field_info(SimpleModel, "name"),
            get_field_info(SimpleModel, "count"),
        ]

        result = generate_field_summary_table(fields, show_alias=True)
        table_content = "\n".join(result)

        # Alias column should not appear when no fields have aliases
        assert "Alias" not in table_content


class TestGenerateRootTypeLine:
    """Tests for generate_root_type_line function."""

    def test_generates_root_type_for_list(self) -> None:
        """Test that root type line is generated for list RootModel."""
        root_field = get_field_info(IntList, "root")

        result = generate_root_type_line(root_field)

        assert isinstance(result, list)
        assert len(result) > 0

        content = "\n".join(result)
        assert "**Root Type:**" in content
        assert "list[int]" in content

    def test_generates_root_type_for_dict(self) -> None:
        """Test that root type line is generated for dict RootModel."""
        root_field = get_field_info(StringMapping, "root")

        result = generate_root_type_line(root_field)

        content = "\n".join(result)
        assert "**Root Type:**" in content
        assert "dict" in content


class TestGenerateValidatorSummaryTable:
    """Tests for generate_validator_summary_table function."""

    def test_generates_table_for_validators(self) -> None:
        """Test that a table is generated for validators."""
        validators = [
            get_validator_info(SingleFieldValidator, "check_positive"),
        ]

        result = generate_validator_summary_table(validators)

        # Check that result is a list of lines
        assert isinstance(result, list)
        assert len(result) > 0

        # Check for table directive
        table_content = "\n".join(result)
        assert ".. list-table:: Validators" in table_content
        assert ":header-rows: 1" in table_content

    def test_includes_validator_names(self) -> None:
        """Test that validator names are included."""
        validators = [
            get_validator_info(SingleFieldValidator, "check_positive"),
        ]

        result = generate_validator_summary_table(validators)
        table_content = "\n".join(result)

        assert "``check_positive``" in table_content

    def test_includes_mode(self) -> None:
        """Test that validator mode is included."""
        validators = [
            get_validator_info(BeforeValidator, "coerce_string"),
        ]

        result = generate_validator_summary_table(validators)
        table_content = "\n".join(result)

        assert "before" in table_content

    def test_includes_fields(self) -> None:
        """Test that validated fields are included."""
        validators = [
            get_validator_info(SingleFieldValidator, "check_positive"),
        ]

        result = generate_validator_summary_table(validators, list_fields=True)
        table_content = "\n".join(result)

        assert "``value``" in table_content

    def test_shows_model_for_model_validators(self) -> None:
        """Test that model validators show 'model' in fields column."""
        validators = [
            get_validator_info(ModelValidatorAfter, "passwords_match"),
        ]

        result = generate_validator_summary_table(validators, list_fields=True)
        table_content = "\n".join(result)

        assert "*model*" in table_content

    def test_returns_empty_for_no_validators(self) -> None:
        """Test that empty list is returned for no validators."""
        result = generate_validator_summary_table([])
        assert result == []


class TestValidatorSummaryWithCrossRefs:
    """Tests for validator summary table with cross-references."""

    def test_generates_validator_xrefs_with_model_path(self) -> None:
        """Test that validator names become cross-references with model_path."""
        validators = [
            get_validator_info(SingleFieldValidator, "check_positive"),
        ]
        model_path = "tests.assets.models.validators.SingleFieldValidator"

        result = generate_validator_summary_table(validators, model_path=model_path)
        table_content = "\n".join(result)

        # Should have :py:obj: reference instead of backticks
        assert ":py:obj:`check_positive <" in table_content
        assert model_path in table_content

    def test_generates_field_xrefs_with_model_path(self) -> None:
        """Test that field names become cross-references with model_path."""
        validators = [
            get_validator_info(SingleFieldValidator, "check_positive"),
        ]
        model_path = "tests.assets.models.validators.SingleFieldValidator"

        result = generate_validator_summary_table(
            validators, list_fields=True, model_path=model_path
        )
        table_content = "\n".join(result)

        # Should have :py:obj: reference for field
        assert ":py:obj:`value <" in table_content

    def test_multi_field_validator_xrefs(self) -> None:
        """Test that multiple fields get cross-references."""
        validators = [
            get_validator_info(MultiFieldValidator, "check_bounds"),
        ]
        model_path = "tests.assets.models.validators.MultiFieldValidator"

        result = generate_validator_summary_table(
            validators, list_fields=True, model_path=model_path
        )
        table_content = "\n".join(result)

        # Both fields should have references
        assert ":py:obj:`x <" in table_content
        assert ":py:obj:`y <" in table_content

    def test_no_xrefs_without_model_path(self) -> None:
        """Test that no cross-references without model_path."""
        validators = [
            get_validator_info(SingleFieldValidator, "check_positive"),
        ]

        result = generate_validator_summary_table(validators)
        table_content = "\n".join(result)

        # Should have backticks, not :py:obj:
        assert "``check_positive``" in table_content
        assert ":py:obj:" not in table_content

    def test_model_validator_no_field_xrefs(self) -> None:
        """Test that model validators show *model* not field xrefs."""
        validators = [
            get_validator_info(ModelValidatorAfter, "passwords_match"),
        ]
        model_path = "tests.assets.models.validators.ModelValidatorAfter"

        result = generate_validator_summary_table(
            validators, list_fields=True, model_path=model_path
        )
        table_content = "\n".join(result)

        # Model validators show *model*, not field references
        assert "*model*" in table_content
