"""Tests for autodoc event handlers."""

from __future__ import annotations

from unittest.mock import MagicMock

from sphinxcontrib.pydantic._autodoc._handlers import (
    _PYDANTIC_BASE_CLASSES,
    PYDANTIC_SKIP_MEMBERS,
    _process_attribute_docstring,
    is_pydantic_base_member,
    is_pydantic_internal,
    should_skip_member,
)
from tests.assets.models.basic import SimpleModel
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


class TestProcessAttributeDocstring:
    """Tests for _process_attribute_docstring function."""

    def test_adds_description_when_docstring_empty(self) -> None:
        """Test that field description is added when docstring is empty."""
        app = MagicMock()
        app.config = MagicMock()
        app.config.sphinxcontrib_pydantic_field_show_constraints = True

        lines: list[str] = []
        _process_attribute_docstring(
            app=app,
            name="tests.assets.models.fields.FieldWithMetadata.documented",
            obj=None,
            options={},
            lines=lines,
        )

        assert "A documented field." in lines

    def test_does_not_replace_existing_docstring(self) -> None:
        """Test that existing docstring content is preserved."""
        app = MagicMock()
        app.config = MagicMock()
        app.config.sphinxcontrib_pydantic_field_show_constraints = True

        lines = ["Existing docstring."]
        _process_attribute_docstring(
            app=app,
            name="tests.assets.models.fields.FieldWithMetadata.documented",
            obj=None,
            options={},
            lines=lines,
        )

        # First line should still be the existing docstring
        assert lines[0] == "Existing docstring."

    def test_adds_constraints_section(self) -> None:
        """Test that constraints are added to docstring."""
        app = MagicMock()
        app.config = MagicMock()
        app.config.sphinxcontrib_pydantic_field_show_constraints = True

        lines: list[str] = []
        _process_attribute_docstring(
            app=app,
            name="tests.assets.models.fields.FieldWithConstraints.bounded",
            obj=None,
            options={},
            lines=lines,
        )

        content = "\n".join(lines)
        assert ":Constraints:" in content
        assert "**ge**" in content
        assert "**le**" in content

    def test_constraints_can_be_disabled(self) -> None:
        """Test that constraints section can be disabled via config."""
        app = MagicMock()
        app.config = MagicMock()
        app.config.sphinxcontrib_pydantic_field_show_constraints = False

        lines: list[str] = []
        _process_attribute_docstring(
            app=app,
            name="tests.assets.models.fields.FieldWithConstraints.bounded",
            obj=None,
            options={},
            lines=lines,
        )

        content = "\n".join(lines)
        assert ":Constraints:" not in content

    def test_adds_validators_section(self) -> None:
        """Test that validators section is added for validated fields."""
        app = MagicMock()
        app.config = MagicMock()
        app.config.sphinxcontrib_pydantic_field_show_constraints = True

        lines: list[str] = []
        _process_attribute_docstring(
            app=app,
            name="tests.assets.models.validators.SingleFieldValidator.value",
            obj=None,
            options={},
            lines=lines,
        )

        content = "\n".join(lines)
        assert ":Validated by:" in content
        assert "check_positive" in content

    def test_ignores_non_pydantic_fields(self) -> None:
        """Test that non-Pydantic model attributes are ignored."""
        app = MagicMock()
        app.config = MagicMock()
        app.config.sphinxcontrib_pydantic_field_show_constraints = True

        lines: list[str] = []
        _process_attribute_docstring(
            app=app,
            name="some.module.SomeClass.some_attr",
            obj=None,
            options={},
            lines=lines,
        )

        # Lines should be empty since the model can't be imported
        assert lines == []

    def test_ignores_non_field_attributes(self) -> None:
        """Test that non-field attributes on Pydantic models are ignored."""
        app = MagicMock()
        app.config = MagicMock()
        app.config.sphinxcontrib_pydantic_field_show_constraints = True

        lines: list[str] = []
        _process_attribute_docstring(
            app=app,
            name="tests.assets.models.basic.SimpleModel.model_fields",
            obj=None,
            options={},
            lines=lines,
        )

        # Lines should be empty since model_fields is not a field
        assert lines == []
