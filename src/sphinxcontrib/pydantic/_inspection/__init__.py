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
from sphinxcontrib.pydantic._inspection._references import (
    ASTERISK_FIELD_NAME,
    ValidatorFieldMap,
    filter_mappings_by_field,
    filter_mappings_by_validator,
    get_validator_field_mappings,
)
from sphinxcontrib.pydantic._inspection._validator import (
    ValidatorInfo,
    get_validator_info,
)
