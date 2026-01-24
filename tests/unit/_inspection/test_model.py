"""Unit tests for model inspection."""

from __future__ import annotations

import pytest
from pydantic import BaseModel
from pydantic_settings import BaseSettings

from sphinxcontrib.pydantic._inspection import (
    ModelInfo,
    get_model_info,
    is_pydantic_model,
    is_pydantic_settings,
    is_root_model,
)
from tests.assets.models.basic import EmptyModel, SimpleModel
from tests.assets.models.computed import ComputedFieldModel
from tests.assets.models.generics import GenericContainer
from tests.assets.models.root_model import ConstrainedIntList, IntList
from tests.assets.models.settings import SimpleSettings
from tests.assets.models.validators import ModelValidatorAfter, SingleFieldValidator


class TestIsPydanticModel:
    """Tests for is_pydantic_model function."""

    def test_returns_true_for_pydantic_model_class(self) -> None:
        """Test that Pydantic model classes are detected."""
        assert is_pydantic_model(SimpleModel) is True

    def test_returns_false_for_pydantic_model_instance(self) -> None:
        """Test that Pydantic model instances are not detected as models."""
        instance = SimpleModel(name="test")
        assert is_pydantic_model(instance) is False

    def test_returns_false_for_regular_class(self) -> None:
        """Test that regular classes are not detected."""

        class RegularClass:
            pass

        assert is_pydantic_model(RegularClass) is False

    def test_returns_false_for_builtin_types(self) -> None:
        """Test that builtin types are not detected."""
        assert is_pydantic_model(str) is False
        assert is_pydantic_model(int) is False
        assert is_pydantic_model(dict) is False
        assert is_pydantic_model(list) is False

    def test_returns_false_for_non_class(self) -> None:
        """Test that non-class objects are not detected."""
        assert is_pydantic_model("string") is False
        assert is_pydantic_model(123) is False
        assert is_pydantic_model(None) is False
        assert is_pydantic_model(lambda x: x) is False

    def test_returns_true_for_inherited_model(self) -> None:
        """Test that inherited models are detected."""

        class ParentModel(BaseModel):
            pass

        class ChildModel(ParentModel):
            pass

        assert is_pydantic_model(ChildModel) is True

    def test_returns_true_for_generic_model(self) -> None:
        """Test that generic models are detected."""
        assert is_pydantic_model(GenericContainer) is True

    def test_returns_true_for_settings_model(self) -> None:
        """Test that BaseSettings models are detected."""
        assert is_pydantic_model(SimpleSettings) is True


class TestGetModelInfo:
    """Tests for get_model_info function."""

    def test_returns_model_info_for_simple_model(self) -> None:
        """Test that ModelInfo is returned for a simple model."""
        info = get_model_info(SimpleModel)

        assert isinstance(info, ModelInfo)
        assert info.name == "SimpleModel"
        assert info.module == "tests.assets.models.basic"
        assert info.qualname == "SimpleModel"

    def test_extracts_docstring(self) -> None:
        """Test that model docstring is extracted."""
        info = get_model_info(SimpleModel)

        assert info.docstring is not None
        assert "Model with basic fields" in info.docstring

    def test_extracts_field_names(self) -> None:
        """Test that field names are extracted."""
        info = get_model_info(SimpleModel)

        assert "name" in info.field_names
        assert "count" in info.field_names

    def test_extracts_validator_names(self) -> None:
        """Test that validator names are extracted."""
        info = get_model_info(SingleFieldValidator)

        assert "check_positive" in info.validator_names

    def test_empty_model_has_no_fields(self) -> None:
        """Test that empty model has no fields."""
        info = get_model_info(EmptyModel)

        assert len(info.field_names) == 0

    def test_raises_for_non_pydantic_model(self) -> None:
        """Test that TypeError is raised for non-Pydantic models."""

        class NotAModel:
            pass

        with pytest.raises(TypeError, match="not a Pydantic model"):
            get_model_info(NotAModel)


class TestModelInfo:
    """Tests for ModelInfo dataclass."""

    def test_has_required_attributes(self) -> None:
        """Test that ModelInfo has all required attributes."""
        info = get_model_info(SimpleModel)

        # Basic attributes
        assert hasattr(info, "name")
        assert hasattr(info, "module")
        assert hasattr(info, "qualname")
        assert hasattr(info, "docstring")

        # Field/validator info
        assert hasattr(info, "field_names")
        assert hasattr(info, "validator_names")

        # Model reference
        assert hasattr(info, "model")

    def test_model_attribute_is_original_class(self) -> None:
        """Test that model attribute references the original class."""
        info = get_model_info(SimpleModel)

        assert info.model is SimpleModel

    def test_computed_field_names_extracted(self) -> None:
        """Test that computed field names are extracted."""
        info = get_model_info(ComputedFieldModel)

        assert "full_name" in info.computed_field_names

    def test_model_validators_extracted(self) -> None:
        """Test that model validators are extracted."""
        info = get_model_info(ModelValidatorAfter)

        assert "passwords_match" in info.model_validator_names


class TestIsPydanticSettings:
    """Tests for is_pydantic_settings function."""

    def test_returns_true_for_settings_class(self) -> None:
        """Test that BaseSettings classes are detected."""
        assert is_pydantic_settings(SimpleSettings) is True

    def test_returns_false_for_regular_model(self) -> None:
        """Test that regular BaseModel classes are not detected as settings."""
        assert is_pydantic_settings(SimpleModel) is False

    def test_returns_false_for_model_instance(self) -> None:
        """Test that settings instances are not detected as settings classes."""
        instance = SimpleSettings()
        assert is_pydantic_settings(instance) is False

    def test_returns_false_for_regular_class(self) -> None:
        """Test that regular classes are not detected."""

        class RegularClass:
            pass

        assert is_pydantic_settings(RegularClass) is False

    def test_returns_false_for_non_class(self) -> None:
        """Test that non-class objects are not detected."""
        assert is_pydantic_settings("string") is False
        assert is_pydantic_settings(123) is False
        assert is_pydantic_settings(None) is False

    def test_returns_true_for_inherited_settings(self) -> None:
        """Test that inherited settings classes are detected."""

        class ChildSettings(BaseSettings):
            pass

        assert is_pydantic_settings(ChildSettings) is True


class TestIsRootModel:
    """Tests for is_root_model function."""

    def test_returns_true_for_root_model_class(self) -> None:
        """Test that RootModel classes are detected."""
        assert is_root_model(IntList) is True

    def test_returns_true_for_root_model_with_validator(self) -> None:
        """Test that RootModel with validators are detected."""
        assert is_root_model(ConstrainedIntList) is True

    def test_returns_false_for_regular_model(self) -> None:
        """Test that regular BaseModel classes are not detected as RootModel."""
        assert is_root_model(SimpleModel) is False

    def test_returns_false_for_settings_model(self) -> None:
        """Test that BaseSettings classes are not detected as RootModel."""
        assert is_root_model(SimpleSettings) is False

    def test_returns_false_for_regular_class(self) -> None:
        """Test that regular classes are not detected."""

        class RegularClass:
            pass

        assert is_root_model(RegularClass) is False

    def test_returns_false_for_non_class(self) -> None:
        """Test that non-class objects are not detected."""
        assert is_root_model("string") is False
        assert is_root_model(123) is False
        assert is_root_model(None) is False

    def test_returns_false_for_root_model_instance(self) -> None:
        """Test that RootModel instances are not detected as RootModel classes."""
        instance = IntList([1, 2, 3])
        assert is_root_model(instance) is False


class TestModelInfoRootModel:
    """Tests for ModelInfo with RootModel."""

    def test_is_root_model_true_for_root_model(self) -> None:
        """Test that is_root_model is True for RootModel classes."""
        info = get_model_info(IntList)

        assert info.is_root_model is True

    def test_is_root_model_false_for_regular_model(self) -> None:
        """Test that is_root_model is False for regular models."""
        info = get_model_info(SimpleModel)

        assert info.is_root_model is False

    def test_root_model_has_root_field(self) -> None:
        """Test that RootModel has a 'root' field."""
        info = get_model_info(IntList)

        assert "root" in info.field_names
        assert len(info.field_names) == 1

    def test_root_model_with_validator_has_validators(self) -> None:
        """Test that RootModel validators are extracted."""
        info = get_model_info(ConstrainedIntList)

        assert "check_positive" in info.validator_names
