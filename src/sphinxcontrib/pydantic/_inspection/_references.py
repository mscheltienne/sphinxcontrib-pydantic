"""Reference mapping utilities for validator-field relationships."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pydantic import BaseModel

#: Display name for model validators that validate the entire model.
ASTERISK_FIELD_NAME = "all fields"


@dataclass(frozen=True, slots=True)
class ValidatorFieldMap:
    """Mapping between a validator and a field it validates.

    Attributes
    ----------
    field_name : str
        Name of the field, or "all fields" for model validators.
    validator_name : str
        Name of the validator function.
    field_ref : str
        Full reference path to field: module.Class.field_name
    validator_ref : str
        Full reference path to validator: module.Class.validator_name
    """

    field_name: str
    validator_name: str
    field_ref: str
    validator_ref: str


def get_defining_class_path(func: object, model: type[BaseModel]) -> str:
    """Get the full path to the class where a method was defined.

    Uses __qualname__ to determine the defining class for inherited methods.

    Parameters
    ----------
    func : object
        The function/method object.
    model : type[BaseModel]
        The model class (used as fallback and for module).

    Returns
    -------
    str
        Full path like 'module.ClassName'.
    """
    qualname = getattr(func, "__qualname__", None)
    module = getattr(func, "__module__", model.__module__)

    if qualname and "." in qualname:
        # Extract class name from qualname like "ClassName.method_name"
        class_name = qualname.rsplit(".", 1)[0]
        return f"{module}.{class_name}"

    # Fallback to the model being documented
    return f"{model.__module__}.{model.__name__}"


def get_field_defining_class_path(field_name: str, model: type[BaseModel]) -> str:
    """Get the full path to the class where a field was defined.

    Walks the MRO to find where the field was first defined.

    Parameters
    ----------
    field_name : str
        The field name.
    model : type[BaseModel]
        The model class.

    Returns
    -------
    str
        Full path like 'module.ClassName'.
    """
    # Walk the MRO to find where this field was first defined
    for cls in model.__mro__:
        if not hasattr(cls, "model_fields"):
            continue
        # Check if this class directly defines the field (not inherited)
        if field_name in cls.__annotations__:
            return f"{cls.__module__}.{cls.__name__}"

    # Fallback to the model being documented
    return f"{model.__module__}.{model.__name__}"


def get_validator_field_mappings(model: type[BaseModel]) -> list[ValidatorFieldMap]:
    """Generate all validator-field mappings for a model.

    Parameters
    ----------
    model : type[BaseModel]
        The Pydantic model class.

    Returns
    -------
    list[ValidatorFieldMap]
        List of all validator-field mappings.
    """
    mappings: list[ValidatorFieldMap] = []
    decorators = model.__pydantic_decorators__
    model_path = f"{model.__module__}.{model.__name__}"

    # Field validators
    for validator_name, validator_decorator in decorators.field_validators.items():
        # Get the class where the validator was defined
        validator_class_path = get_defining_class_path(
            validator_decorator.func, model
        )

        for field in validator_decorator.info.fields:
            field_name = ASTERISK_FIELD_NAME if field == "*" else field

            # Get the class where the field was defined
            if field_name == ASTERISK_FIELD_NAME:
                field_class_path = model_path
            else:
                field_class_path = get_field_defining_class_path(field_name, model)

            mappings.append(
                ValidatorFieldMap(
                    field_name=field_name,
                    validator_name=validator_name,
                    field_ref=f"{field_class_path}.{field_name}",
                    validator_ref=f"{validator_class_path}.{validator_name}",
                )
            )

    # Model validators (validate "all fields")
    for validator_name, validator_decorator in decorators.model_validators.items():
        validator_class_path = get_defining_class_path(
            validator_decorator.func, model
        )
        mappings.append(
            ValidatorFieldMap(
                field_name=ASTERISK_FIELD_NAME,
                validator_name=validator_name,
                field_ref=f"{model_path}.{ASTERISK_FIELD_NAME}",
                validator_ref=f"{validator_class_path}.{validator_name}",
            )
        )

    return mappings


def filter_mappings_by_validator(
    mappings: list[ValidatorFieldMap],
    validator_name: str,
) -> list[ValidatorFieldMap]:
    """Filter mappings to those for a specific validator.

    Parameters
    ----------
    mappings : list[ValidatorFieldMap]
        The mappings to filter.
    validator_name : str
        The validator name to filter by.

    Returns
    -------
    list[ValidatorFieldMap]
        Mappings where validator_name matches.
    """
    return [m for m in mappings if m.validator_name == validator_name]


def filter_mappings_by_field(
    mappings: list[ValidatorFieldMap],
    field_name: str,
) -> list[ValidatorFieldMap]:
    """Filter mappings to those for a specific field.

    Includes model validators (which apply to "all fields").

    Parameters
    ----------
    mappings : list[ValidatorFieldMap]
        The mappings to filter.
    field_name : str
        The field name to filter by.

    Returns
    -------
    list[ValidatorFieldMap]
        Mappings where field_name matches or is "all fields".
    """
    return [m for m in mappings if m.field_name in (field_name, ASTERISK_FIELD_NAME)]
