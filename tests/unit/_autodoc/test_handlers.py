"""Tests for autodoc event handlers."""

from __future__ import annotations

from unittest.mock import MagicMock

from sphinxcontrib.pydantic._autodoc._handlers import (
    _PYDANTIC_BASE_CLASSES,
    PYDANTIC_SKIP_MEMBERS,
    _generate_field_documentation,
    is_pydantic_base_member,
    is_pydantic_internal,
    should_skip_member,
)
from sphinxcontrib.pydantic._inspection import get_model_info
from tests.assets.models.basic import SimpleModel
from tests.assets.models.fields import (
    FieldWithConstraints,
    FieldWithDefaults,
    FieldWithMetadata,
)
from tests.assets.models.sqlmodel_models import HeroCreate
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

    def test_skips_inherited_basemodel_methods(self) -> None:
        """Test that inherited BaseModel methods are skipped."""
        result = should_skip_member(
            what="method",
            name="model_dump",
            obj=SimpleModel.model_dump,
            skip=False,
            options={},
        )
        # Inherited BaseModel methods should be skipped
        assert result is True

    def test_skips_inherited_basemodel_classmethods(self) -> None:
        """Test that inherited BaseModel classmethods are skipped."""
        result = should_skip_member(
            what="method",
            name="model_validate",
            obj=SimpleModel.model_validate,
            skip=False,
            options={},
        )
        # Inherited BaseModel classmethods should be skipped
        assert result is True

    def test_does_not_skip_user_defined_methods(self) -> None:
        """Test that user-defined methods are not skipped."""
        result = should_skip_member(
            what="method",
            name="check_positive",
            obj=SingleFieldValidator.check_positive,
            skip=False,
            options={},
        )
        # User-defined methods should not be skipped
        assert result is None

    def test_skips_inherited_sqlmodel_methods(self) -> None:
        """Test that inherited SQLModel methods are skipped."""
        result = should_skip_member(
            what="method",
            name="model_dump",
            obj=HeroCreate.model_dump,
            skip=False,
            options={},
        )
        # Inherited SQLModel methods should be skipped
        assert result is True


class TestIsPydanticBaseMember:
    """Tests for is_pydantic_base_member function."""

    def test_basemodel_method_is_base_member(self) -> None:
        """Test that BaseModel methods are detected as base members."""
        assert is_pydantic_base_member(SimpleModel.model_dump) is True

    def test_basemodel_classmethod_is_base_member(self) -> None:
        """Test that BaseModel classmethods are detected as base members."""
        assert is_pydantic_base_member(SimpleModel.model_validate) is True

    def test_basemodel_model_construct_is_base_member(self) -> None:
        """Test that model_construct is detected as base member."""
        assert is_pydantic_base_member(SimpleModel.model_construct) is True

    def test_basemodel_model_copy_is_base_member(self) -> None:
        """Test that model_copy is detected as base member."""
        assert is_pydantic_base_member(SimpleModel.model_copy) is True

    def test_sqlmodel_method_is_base_member(self) -> None:
        """Test that SQLModel methods are detected as base members."""
        assert is_pydantic_base_member(HeroCreate.model_dump) is True

    def test_sqlmodel_classmethod_is_base_member(self) -> None:
        """Test that SQLModel classmethods are detected as base members."""
        assert is_pydantic_base_member(HeroCreate.model_validate) is True

    def test_user_defined_method_not_base_member(self) -> None:
        """Test that user-defined methods are not detected as base members."""
        assert is_pydantic_base_member(SingleFieldValidator.check_positive) is False

    def test_string_not_base_member(self) -> None:
        """Test that non-callable objects return False."""
        assert is_pydantic_base_member("some_string") is False

    def test_none_not_base_member(self) -> None:
        """Test that None returns False."""
        assert is_pydantic_base_member(None) is False


class TestPydanticBaseClasses:
    """Tests for the _PYDANTIC_BASE_CLASSES constant."""

    def test_contains_basemodel(self) -> None:
        """Test that BaseModel is in the base classes."""
        assert "BaseModel" in _PYDANTIC_BASE_CLASSES

    def test_contains_sqlmodel(self) -> None:
        """Test that SQLModel is in the base classes."""
        assert "SQLModel" in _PYDANTIC_BASE_CLASSES


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

    def test_skip_members_contains_all_expected(self) -> None:
        """Test that PYDANTIC_SKIP_MEMBERS contains all known internals."""
        expected_members = {
            # Model class attributes
            "model_fields",
            "model_computed_fields",
            "model_config",
            "model_extra",
            "model_fields_set",
            # Private pydantic attributes
            "__pydantic_complete__",
            "__pydantic_core_schema__",
            "__pydantic_custom_init__",
            "__pydantic_decorators__",
            "__pydantic_extra__",
            "__pydantic_fields_set__",
            "__pydantic_generic_metadata__",
            "__pydantic_parent_namespace__",
            "__pydantic_post_init__",
            "__pydantic_private__",
            "__pydantic_root_model__",
            "__pydantic_serializer__",
            "__pydantic_validator__",
            # Class variables from pydantic
            "__class_vars__",
            "__private_attributes__",
            "__signature__",
            "__pydantic_fields__",
        }
        assert expected_members <= PYDANTIC_SKIP_MEMBERS


class TestGenerateFieldDocumentation:
    """Tests for _generate_field_documentation function."""

    def test_generates_field_directive_for_each_field(self) -> None:
        """Test that a field directive is generated for each model field."""
        model_info = get_model_info(SimpleModel)
        app = MagicMock()

        result = _generate_field_documentation(SimpleModel, model_info, app)

        content = "\n".join(result)
        # Should have field directives for both fields
        assert ".. py:pydantic_field:: name" in content
        assert ".. py:pydantic_field:: count" in content

    def test_includes_required_option_for_required_fields(self) -> None:
        """Test that required fields have :required: option."""
        model_info = get_model_info(FieldWithDefaults)
        app = MagicMock()

        result = _generate_field_documentation(FieldWithDefaults, model_info, app)

        content = "\n".join(result)
        # required_field should have :required:
        assert ".. py:pydantic_field:: required_field" in content
        assert ":required:" in content

    def test_includes_optional_option_for_optional_fields(self) -> None:
        """Test that optional fields have :optional: option."""
        model_info = get_model_info(FieldWithDefaults)
        app = MagicMock()

        result = _generate_field_documentation(FieldWithDefaults, model_info, app)

        content = "\n".join(result)
        # optional_field should have :optional:
        assert ".. py:pydantic_field:: optional_field" in content
        assert ":optional:" in content

    def test_includes_type_annotation(self) -> None:
        """Test that type annotation is included."""
        model_info = get_model_info(SimpleModel)
        app = MagicMock()

        result = _generate_field_documentation(SimpleModel, model_info, app)

        content = "\n".join(result)
        assert ":type: str" in content
        assert ":type: int" in content

    def test_includes_default_value(self) -> None:
        """Test that default values are included."""
        model_info = get_model_info(FieldWithDefaults)
        app = MagicMock()

        result = _generate_field_documentation(FieldWithDefaults, model_info, app)

        content = "\n".join(result)
        # default_value has default of 42
        assert ":value: 42" in content

    def test_includes_factory_default(self) -> None:
        """Test that factory defaults are indicated."""
        model_info = get_model_info(FieldWithDefaults)
        app = MagicMock()

        result = _generate_field_documentation(FieldWithDefaults, model_info, app)

        content = "\n".join(result)
        # factory_default uses default_factory
        assert ":value: *factory*" in content

    def test_includes_field_description(self) -> None:
        """Test that field description is included."""
        model_info = get_model_info(FieldWithMetadata)
        app = MagicMock()

        result = _generate_field_documentation(FieldWithMetadata, model_info, app)

        content = "\n".join(result)
        assert "A documented field." in content

    def test_includes_constraints(self) -> None:
        """Test that constraints are included."""
        model_info = get_model_info(FieldWithConstraints)
        app = MagicMock()

        result = _generate_field_documentation(FieldWithConstraints, model_info, app)

        content = "\n".join(result)
        # bounded field has ge=0, le=100
        assert ":Constraints:" in content
        assert "**ge** = 0" in content
        assert "**le** = 100" in content

    def test_includes_validators(self) -> None:
        """Test that validators are referenced."""
        model_info = get_model_info(SingleFieldValidator)
        app = MagicMock()

        result = _generate_field_documentation(SingleFieldValidator, model_info, app)

        content = "\n".join(result)
        # value field is validated by check_positive
        assert ":Validated by:" in content
        assert "check_positive" in content

    def test_returns_empty_for_no_fields(self) -> None:
        """Test that empty list is returned for model with no fields."""
        from pydantic import BaseModel

        class EmptyModel(BaseModel):
            pass

        model_info = get_model_info(EmptyModel)
        app = MagicMock()

        result = _generate_field_documentation(EmptyModel, model_info, app)

        assert result == []
