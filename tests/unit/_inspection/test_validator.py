"""Unit tests for validator inspection."""

from __future__ import annotations

import pytest

from sphinxcontrib.pydantic._inspection import ValidatorInfo, get_validator_info
from tests.assets.models.validators import (
    BeforeValidator,
    ModelValidatorAfter,
    ModelValidatorBefore,
    MultiFieldValidator,
    SingleFieldValidator,
    WrapValidator,
)


class TestGetValidatorInfo:
    """Tests for get_validator_info function."""

    def test_returns_validator_info(self) -> None:
        """Test that ValidatorInfo is returned for a field validator."""
        info = get_validator_info(SingleFieldValidator, "check_positive")

        assert isinstance(info, ValidatorInfo)
        assert info.name == "check_positive"

    def test_extracts_validated_fields(self) -> None:
        """Test that validated fields are extracted."""
        info = get_validator_info(SingleFieldValidator, "check_positive")

        assert info.fields == ("value",)
        assert info.is_model_validator is False
        assert info.mode == "after"  # Verify default mode

    def test_extracts_multiple_validated_fields(self) -> None:
        """Test that multiple validated fields are extracted."""
        info = get_validator_info(MultiFieldValidator, "check_bounds")

        assert set(info.fields) == {"x", "y"}

    def test_extracts_validator_mode(self) -> None:
        """Test that validator mode is extracted."""
        info = get_validator_info(BeforeValidator, "coerce_string")

        assert info.mode == "before"

    def test_default_mode_is_after(self) -> None:
        """Test that default mode is 'after'."""
        info = get_validator_info(SingleFieldValidator, "check_positive")

        assert info.mode == "after"

    def test_extracts_wrap_mode(self) -> None:
        """Test that wrap mode is extracted."""
        info = get_validator_info(WrapValidator, "wrap_value")

        assert info.mode == "wrap"
        assert info.fields == ("value",)
        assert info.is_model_validator is False

    def test_extracts_docstring(self) -> None:
        """Test that validator docstring is extracted."""
        info = get_validator_info(SingleFieldValidator, "check_positive")

        assert info.docstring is not None
        assert "Ensure value is positive" in info.docstring

    def test_raises_for_invalid_validator(self) -> None:
        """Test that KeyError is raised for non-existent validators."""
        with pytest.raises(KeyError, match="not_a_validator"):
            get_validator_info(SingleFieldValidator, "not_a_validator")

    def test_raises_for_non_pydantic_model(self) -> None:
        """Test that TypeError is raised for non-Pydantic models."""

        class NotAModel:
            pass

        with pytest.raises(TypeError, match="not a Pydantic model"):
            get_validator_info(NotAModel, "validator")


class TestModelValidatorInfo:
    """Tests for model validator inspection."""

    def test_extracts_model_validator_after(self) -> None:
        """Test that model validators with mode='after' are extracted."""
        info = get_validator_info(ModelValidatorAfter, "passwords_match")

        assert info.is_model_validator is True
        assert info.mode == "after"

    def test_extracts_model_validator_before(self) -> None:
        """Test that model validators with mode='before' are extracted."""
        info = get_validator_info(ModelValidatorBefore, "ensure_dict")

        assert info.is_model_validator is True
        assert info.mode == "before"

    def test_model_validator_has_no_fields(self) -> None:
        """Test that model validators have no specific fields."""
        info = get_validator_info(ModelValidatorAfter, "passwords_match")

        # Model validators validate the whole model, not specific fields
        assert info.fields == ()


class TestValidatorInfo:
    """Tests for ValidatorInfo dataclass."""

    def test_has_required_attributes(self) -> None:
        """Test that ValidatorInfo has all required attributes."""
        info = get_validator_info(SingleFieldValidator, "check_positive")

        # Basic attributes
        assert hasattr(info, "name")
        assert hasattr(info, "fields")
        assert hasattr(info, "mode")
        assert hasattr(info, "docstring")
        assert hasattr(info, "is_model_validator")
