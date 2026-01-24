"""Unit tests for reference mapping utilities."""

from __future__ import annotations

import pytest

from sphinxcontrib.pydantic._inspection import (
    ASTERISK_FIELD_NAME,
    ValidatorFieldMap,
    filter_mappings_by_field,
    filter_mappings_by_validator,
    get_validator_field_mappings,
)


class TestValidatorFieldMap:
    """Tests for ValidatorFieldMap dataclass."""

    def test_has_required_attributes(self) -> None:
        """Test that ValidatorFieldMap has all required attributes."""
        mapping = ValidatorFieldMap(
            field_name="field",
            validator_name="validator",
            field_ref="module.Class.field",
            validator_ref="module.Class.validator",
        )

        assert mapping.field_name == "field"
        assert mapping.validator_name == "validator"
        assert mapping.field_ref == "module.Class.field"
        assert mapping.validator_ref == "module.Class.validator"

    def test_is_frozen(self) -> None:
        """Test that ValidatorFieldMap is immutable."""
        mapping = ValidatorFieldMap(
            field_name="field",
            validator_name="validator",
            field_ref="module.Class.field",
            validator_ref="module.Class.validator",
        )

        with pytest.raises(AttributeError):
            mapping.field_name = "other"  # type: ignore[misc]


class TestGetValidatorFieldMappings:
    """Tests for get_validator_field_mappings function."""

    def test_single_field_validator(self) -> None:
        """Test mapping for a single field validator."""
        from tests.assets.models.validators import SingleFieldValidator

        mappings = get_validator_field_mappings(SingleFieldValidator)

        assert len(mappings) == 1
        mapping = mappings[0]
        assert mapping.field_name == "value"
        assert mapping.validator_name == "check_positive"
        assert "SingleFieldValidator.value" in mapping.field_ref
        assert "SingleFieldValidator.check_positive" in mapping.validator_ref

    def test_multi_field_validator(self) -> None:
        """Test mapping for a validator on multiple fields."""
        from tests.assets.models.validators import MultiFieldValidator

        mappings = get_validator_field_mappings(MultiFieldValidator)

        assert len(mappings) == 2
        field_names = {m.field_name for m in mappings}
        assert field_names == {"x", "y"}

        # All mappings should reference the same validator
        validator_names = {m.validator_name for m in mappings}
        assert validator_names == {"check_bounds"}

    def test_model_validator_uses_asterisk_name(self) -> None:
        """Test that model validators use ASTERISK_FIELD_NAME."""
        from tests.assets.models.validators import ModelValidatorAfter

        mappings = get_validator_field_mappings(ModelValidatorAfter)

        assert len(mappings) == 1
        mapping = mappings[0]
        assert mapping.field_name == ASTERISK_FIELD_NAME
        assert mapping.validator_name == "passwords_match"

    def test_model_with_no_validators(self) -> None:
        """Test that models without validators return empty list."""
        from tests.assets.models.basic import SimpleModel

        mappings = get_validator_field_mappings(SimpleModel)

        assert mappings == []

    def test_field_ref_format(self) -> None:
        """Test that field_ref has correct format."""
        from tests.assets.models.validators import SingleFieldValidator

        mappings = get_validator_field_mappings(SingleFieldValidator)

        mapping = mappings[0]
        # Should be: module.ClassName.field_name
        expected = "tests.assets.models.validators.SingleFieldValidator.value"
        assert mapping.field_ref == expected

    def test_validator_ref_format(self) -> None:
        """Test that validator_ref has correct format."""
        from tests.assets.models.validators import SingleFieldValidator

        mappings = get_validator_field_mappings(SingleFieldValidator)

        mapping = mappings[0]
        # Should be: module.ClassName.validator_name
        expected = "tests.assets.models.validators.SingleFieldValidator.check_positive"
        assert mapping.validator_ref == expected


class TestFilterMappingsByValidator:
    """Tests for filter_mappings_by_validator function."""

    def test_filters_by_validator_name(self) -> None:
        """Test filtering mappings by validator name."""
        from tests.assets.models.validators import MultiFieldValidator

        mappings = get_validator_field_mappings(MultiFieldValidator)
        filtered = filter_mappings_by_validator(mappings, "check_bounds")

        assert len(filtered) == 2

    def test_returns_empty_for_nonexistent_validator(self) -> None:
        """Test that filtering returns empty list for nonexistent validator."""
        from tests.assets.models.validators import SingleFieldValidator

        mappings = get_validator_field_mappings(SingleFieldValidator)
        filtered = filter_mappings_by_validator(mappings, "nonexistent")

        assert filtered == []


class TestFilterMappingsByField:
    """Tests for filter_mappings_by_field function."""

    def test_filters_by_field_name(self) -> None:
        """Test filtering mappings by field name."""
        from tests.assets.models.validators import SingleFieldValidator

        mappings = get_validator_field_mappings(SingleFieldValidator)
        filtered = filter_mappings_by_field(mappings, "value")

        assert len(filtered) == 1
        assert filtered[0].field_name == "value"

    def test_includes_model_validators(self) -> None:
        """Test that filtering includes model validators (all fields)."""
        from tests.assets.models.validators import ModelValidatorAfter

        mappings = get_validator_field_mappings(ModelValidatorAfter)
        # Model validator should match any field
        filtered = filter_mappings_by_field(mappings, "password")

        assert len(filtered) == 1
        assert filtered[0].field_name == ASTERISK_FIELD_NAME

    def test_returns_empty_for_nonexistent_field(self) -> None:
        """Test that filtering returns empty for nonexistent field."""
        from tests.assets.models.validators import SingleFieldValidator

        mappings = get_validator_field_mappings(SingleFieldValidator)
        filtered = filter_mappings_by_field(mappings, "nonexistent")

        assert filtered == []


class TestInheritanceScenarios:
    """Tests for validator mappings with inheritance."""

    def test_child_inherits_parent_validators(self) -> None:
        """Test that child model includes inherited validators."""
        from tests.assets.models.inheritance import ChildModelSimple

        mappings = get_validator_field_mappings(ChildModelSimple)

        # Should have the inherited validator
        validator_names = {m.validator_name for m in mappings}
        assert "validate_base_field" in validator_names

        # Verify the ref points to the defining class (where validator is documented)
        inherited_mapping = next(
            m for m in mappings if m.validator_name == "validate_base_field"
        )
        assert "BaseModelWithValidator" in inherited_mapping.validator_ref
        assert "BaseModelWithValidator" in inherited_mapping.field_ref

    def test_child_with_own_and_inherited_validators(self) -> None:
        """Test child model with both own and inherited validators."""
        from tests.assets.models.inheritance import ChildModelWithOwnValidator

        mappings = get_validator_field_mappings(ChildModelWithOwnValidator)

        validator_names = {m.validator_name for m in mappings}
        assert "validate_base_field" in validator_names
        assert "validate_child_field" in validator_names

    def test_grandchild_inheritance(self) -> None:
        """Test three-level inheritance."""
        from tests.assets.models.inheritance import GrandchildModel

        mappings = get_validator_field_mappings(GrandchildModel)

        validator_names = {m.validator_name for m in mappings}
        assert "validate_base_field" in validator_names
        assert "validate_child_field" in validator_names
        assert "validate_grandchild" in validator_names
