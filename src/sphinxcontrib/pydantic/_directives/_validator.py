"""Pydantic validator documentation directive."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from docutils.parsers.rst import directives

from sphinxcontrib.pydantic._directives._base import PydanticDirective, flag_or_value

if TYPE_CHECKING:
    from typing import Any


class PydanticValidatorDirective(PydanticDirective):
    """Directive for documenting a Pydantic validator.

    Usage::

        .. pydantic-validator:: validator_name
           :module: mymodule
           :model: MyModel
           :list-fields:
    """

    option_spec: ClassVar[dict[str, Any]] = {
        # Inherited from base
        "module": directives.unchanged,
        "noindex": directives.flag,
        # Validator-specific options
        "model": directives.unchanged_required,
        "list-fields": flag_or_value,
    }
