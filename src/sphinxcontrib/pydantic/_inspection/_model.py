"""Model inspection utilities for Pydantic v2 models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from typing import Any


def is_pydantic_model(obj: Any) -> bool:
    """Check if an object is a Pydantic model class.

    Parameters
    ----------
    obj : Any
        The object to check.

    Returns
    -------
    bool
        True if the object is a Pydantic model class, False otherwise.

    Notes
    -----
    This function checks if the object is a class (not an instance) that
    inherits from ``pydantic.BaseModel``. Instances of Pydantic models
    will return False.
    """
    try:
        return isinstance(obj, type) and issubclass(obj, BaseModel)
    except TypeError:
        # issubclass raises TypeError for non-class objects
        return False


@dataclass(frozen=True, slots=True)
class ModelInfo:
    """Information about a Pydantic model.

    Attributes
    ----------
    name : str
        The name of the model class.
    module : str
        The module where the model is defined.
    qualname : str
        The qualified name of the model class.
    docstring : str | None
        The docstring of the model, if any.
    field_names : tuple[str, ...]
        Names of all regular fields in the model.
    computed_field_names : tuple[str, ...]
        Names of all computed fields in the model.
    validator_names : tuple[str, ...]
        Names of all field validators in the model.
    model_validator_names : tuple[str, ...]
        Names of all model validators in the model.
    model : type[BaseModel]
        Reference to the original model class.
    """

    name: str
    module: str
    qualname: str
    docstring: str | None
    field_names: tuple[str, ...] = field(default_factory=tuple)
    computed_field_names: tuple[str, ...] = field(default_factory=tuple)
    validator_names: tuple[str, ...] = field(default_factory=tuple)
    model_validator_names: tuple[str, ...] = field(default_factory=tuple)
    model: type[BaseModel] = field(repr=False, default=None)


def get_model_info(model: type[BaseModel]) -> ModelInfo:
    """Extract information from a Pydantic model.

    Parameters
    ----------
    model : type[BaseModel]
        The Pydantic model class to inspect.

    Returns
    -------
    ModelInfo
        Information about the model.

    Raises
    ------
    TypeError
        If the provided object is not a Pydantic model class.
    """
    if not is_pydantic_model(model):
        raise TypeError(f"{model!r} is not a Pydantic model class.")

    # Extract basic information
    name = model.__name__
    module = model.__module__
    qualname = model.__qualname__
    docstring = model.__doc__

    # Extract field names
    field_names = tuple(model.model_fields.keys())

    # Extract computed field names
    computed_field_names = tuple(model.model_computed_fields.keys())

    # Extract validator names from pydantic decorators
    decorators = model.__pydantic_decorators__
    validator_names = list(decorators.field_validators.keys())
    model_validator_names = list(decorators.model_validators.keys())

    return ModelInfo(
        name=name,
        module=module,
        qualname=qualname,
        docstring=docstring,
        field_names=field_names,
        computed_field_names=tuple(computed_field_names),
        validator_names=tuple(validator_names),
        model_validator_names=tuple(model_validator_names),
        model=model,
    )
