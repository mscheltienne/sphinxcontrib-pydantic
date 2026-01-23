"""Pydantic model introspection utilities.

This module provides utilities for introspecting Pydantic v2 models,
extracting field information, validators, and other metadata.
"""

from sphinxcontrib.pydantic._inspection._field import FieldInfo, get_field_info
from sphinxcontrib.pydantic._inspection._model import (
    ModelInfo,
    get_model_info,
    is_pydantic_model,
    is_pydantic_settings,
)
from sphinxcontrib.pydantic._inspection._schema import (
    SchemaInfo,
    generate_json_schema,
    get_schema_info,
)
from sphinxcontrib.pydantic._inspection._validator import (
    ValidatorInfo,
    get_validator_info,
)
