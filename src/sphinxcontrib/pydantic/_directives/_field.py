"""Pydantic field documentation directive."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from docutils.parsers.rst import directives

from sphinxcontrib.pydantic._directives._base import PydanticDirective, flag_or_value

if TYPE_CHECKING:
    from typing import Any


class PydanticFieldDirective(PydanticDirective):
    """Directive for documenting a Pydantic model field.

    Usage::

        .. pydantic-field:: field_name
           :module: mymodule
           :model: MyModel
           :show-alias:
           :show-default:
           :show-constraints:
    """

    option_spec: ClassVar[dict[str, Any]] = {
        # Inherited from base
        "module": directives.unchanged,
        "noindex": directives.flag,
        # Field-specific options
        "model": directives.unchanged_required,
        "show-alias": flag_or_value,
        "show-default": flag_or_value,
        "show-constraints": flag_or_value,
    }
