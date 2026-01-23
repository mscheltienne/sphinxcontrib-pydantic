"""Unit tests for summary table generation."""

from __future__ import annotations

from sphinxcontrib.pydantic._inspection import get_field_info, get_validator_info
from sphinxcontrib.pydantic._rendering import (
    generate_field_summary_table,
    generate_validator_summary_table,
)


class TestGenerateFieldSummaryTable:
    """Tests for generate_field_summary_table function."""

    def test_generates_table_for_simple_model(self) -> None:
        """Test that a table is generated for a simple model."""
        from tests.assets.models.basic import SimpleModel

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
        from tests.assets.models.basic import SimpleModel

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
        from tests.assets.models.basic import SimpleModel

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
        from tests.assets.models.basic import SimpleModel

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
        from tests.assets.models.basic import SimpleModel

        fields = [
            get_field_info(SimpleModel, "count"),
        ]

        result = generate_field_summary_table(fields, show_default=True)
        table_content = "\n".join(result)

        assert "``0``" in table_content

    def test_includes_aliases(self) -> None:
        """Test that aliases are included when present."""
        from tests.assets.models.fields import FieldWithAlias

        fields = [
            get_field_info(FieldWithAlias, "internal_name"),
        ]

        result = generate_field_summary_table(fields, show_alias=True)
        table_content = "\n".join(result)

        assert "Alias" in table_content
        assert "``externalName``" in table_content

    def test_includes_constraints(self) -> None:
        """Test that constraints are included when present."""
        from tests.assets.models.fields import FieldWithConstraints

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
        from tests.assets.models.basic import SimpleModel

        fields = [
            get_field_info(SimpleModel, "name"),
            get_field_info(SimpleModel, "count"),
        ]

        result = generate_field_summary_table(fields, show_alias=True)
        table_content = "\n".join(result)

        # Alias column should not appear when no fields have aliases
        assert "Alias" not in table_content


class TestGenerateValidatorSummaryTable:
    """Tests for generate_validator_summary_table function."""

    def test_generates_table_for_validators(self) -> None:
        """Test that a table is generated for validators."""
        from tests.assets.models.validators import SingleFieldValidator

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
        from tests.assets.models.validators import SingleFieldValidator

        validators = [
            get_validator_info(SingleFieldValidator, "check_positive"),
        ]

        result = generate_validator_summary_table(validators)
        table_content = "\n".join(result)

        assert "``check_positive``" in table_content

    def test_includes_mode(self) -> None:
        """Test that validator mode is included."""
        from tests.assets.models.validators import BeforeValidator

        validators = [
            get_validator_info(BeforeValidator, "coerce_string"),
        ]

        result = generate_validator_summary_table(validators)
        table_content = "\n".join(result)

        assert "before" in table_content

    def test_includes_fields(self) -> None:
        """Test that validated fields are included."""
        from tests.assets.models.validators import SingleFieldValidator

        validators = [
            get_validator_info(SingleFieldValidator, "check_positive"),
        ]

        result = generate_validator_summary_table(validators, list_fields=True)
        table_content = "\n".join(result)

        assert "``value``" in table_content

    def test_shows_model_for_model_validators(self) -> None:
        """Test that model validators show 'model' in fields column."""
        from tests.assets.models.validators import ModelValidatorAfter

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
