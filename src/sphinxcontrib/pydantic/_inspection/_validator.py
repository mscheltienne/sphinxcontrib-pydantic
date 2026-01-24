"""Validator inspection utilities for Pydantic v2 models."""

from __future__ import annotations

from dataclasses import dataclass

from pydantic import BaseModel
from sphinxcontrib.pydantic._inspection._model import is_pydantic_model
from sphinxcontrib.pydantic._inspection._references import (
    get_defining_class_path,
    get_field_defining_class_path,
)


@dataclass(frozen=True, slots=True)
class ValidatorInfo:
    """Information about a Pydantic validator.

    Attributes
    ----------
    name : str
        The name of the validator function.
    fields : tuple[str, ...]
        The fields that this validator validates. Empty for model validators.
    mode : str
        The validation mode ('before', 'after', 'wrap', 'plain').
    docstring : str | None
        The docstring of the validator function, if any.
    is_model_validator : bool
        Whether this is a model validator (vs field validator).
    defining_class_path : str
        Full path to the class where this validator was defined
        (e.g., "module.ClassName"). Used for cross-references.
    field_class_paths : dict[str, str]
        Mapping of field name to the class path where that field was defined.
        Used for cross-references to inherited fields.
    """

    name: str
    fields: tuple[str, ...]
    mode: str
    docstring: str | None
    is_model_validator: bool
    defining_class_path: str
    field_class_paths: dict[str, str]


def get_validator_info(model: type[BaseModel], validator_name: str) -> ValidatorInfo:
    """Extract information about a specific validator from a Pydantic model.

    Parameters
    ----------
    model : type[BaseModel]
        The Pydantic model class.
    validator_name : str
        The name of the validator to inspect.

    Returns
    -------
    ValidatorInfo
        Information about the validator.

    Raises
    ------
    TypeError
        If the provided object is not a Pydantic model class.
    KeyError
        If the validator does not exist in the model.
    """
    if not is_pydantic_model(model):
        raise TypeError(f"{model!r} is not a Pydantic model class.")

    decorators = model.__pydantic_decorators__

    # Check field validators first
    if validator_name in decorators.field_validators:
        return _get_field_validator_info(model, validator_name, decorators)

    # Check model validators
    if validator_name in decorators.model_validators:
        return _get_model_validator_info(model, validator_name, decorators)

    raise KeyError(
        f"Validator '{validator_name}' does not exist in model {model.__name__}"
    )


def _get_field_validator_info(
    model: type[BaseModel],
    validator_name: str,
    decorators,
) -> ValidatorInfo:
    """Extract information about a field validator.

    Parameters
    ----------
    model : type[BaseModel]
        The Pydantic model class.
    validator_name : str
        The name of the validator.
    decorators
        The model's pydantic decorators.

    Returns
    -------
    ValidatorInfo
        Information about the field validator.
    """
    validator_decorator = decorators.field_validators[validator_name]

    # Get the fields this validator validates
    fields = tuple(validator_decorator.info.fields)

    # Get the mode (default is 'after')
    mode = validator_decorator.info.mode

    # Get the docstring from the function
    func = validator_decorator.func
    docstring = func.__doc__

    # Get the defining class path for the validator
    defining_class_path = get_defining_class_path(func, model)

    # Get defining class paths for each field
    field_class_paths = {
        f: get_field_defining_class_path(f, model)
        for f in fields
        if f != "*"  # Skip wildcard field
    }

    return ValidatorInfo(
        name=validator_name,
        fields=fields,
        mode=mode,
        docstring=docstring,
        is_model_validator=False,
        defining_class_path=defining_class_path,
        field_class_paths=field_class_paths,
    )


def _get_model_validator_info(
    model: type[BaseModel],
    validator_name: str,
    decorators,
) -> ValidatorInfo:
    """Extract information about a model validator.

    Parameters
    ----------
    model : type[BaseModel]
        The Pydantic model class.
    validator_name : str
        The name of the validator.
    decorators
        The model's pydantic decorators.

    Returns
    -------
    ValidatorInfo
        Information about the model validator.
    """
    validator_decorator = decorators.model_validators[validator_name]

    # Model validators don't have specific fields
    fields: tuple[str, ...] = ()

    # Get the mode
    mode = validator_decorator.info.mode

    # Get the docstring from the function
    func = validator_decorator.func
    docstring = func.__doc__

    # Get the defining class path for the validator
    defining_class_path = get_defining_class_path(func, model)

    return ValidatorInfo(
        name=validator_name,
        fields=fields,
        mode=mode,
        docstring=docstring,
        is_model_validator=True,
        defining_class_path=defining_class_path,
        field_class_paths={},  # Model validators don't reference specific fields
    )
