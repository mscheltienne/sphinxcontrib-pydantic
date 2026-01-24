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
        for field in validator_decorator.info.fields:
            field_name = ASTERISK_FIELD_NAME if field == "*" else field
            mappings.append(
                ValidatorFieldMap(
                    field_name=field_name,
                    validator_name=validator_name,
                    field_ref=f"{model_path}.{field_name}",
                    validator_ref=f"{model_path}.{validator_name}",
                )
            )

    # Model validators (validate "all fields")
    mappings.extend(
        ValidatorFieldMap(
            field_name=ASTERISK_FIELD_NAME,
            validator_name=validator_name,
            field_ref=f"{model_path}.{ASTERISK_FIELD_NAME}",
            validator_ref=f"{model_path}.{validator_name}",
        )
        for validator_name in decorators.model_validators
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
