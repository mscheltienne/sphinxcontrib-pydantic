"""Directive for documenting Pydantic model fields."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from docutils.parsers.rst import directives
from sphinx import addnodes
from sphinx.domains.python import PyAttribute
from sphinx.locale import _

if TYPE_CHECKING:
    from collections.abc import Sequence

    from docutils.nodes import Node
    from sphinx.addnodes import desc_signature
    from sphinx.util.typing import OptionSpec


class PydanticFieldDirective(PyAttribute):
    """Directive for documenting Pydantic model fields.

    This directive extends PyAttribute to provide specialized documentation
    for Pydantic fields, including a "field" prefix and [Required]/[Optional]
    markers in the signature.
    """

    option_spec: ClassVar[OptionSpec] = PyAttribute.option_spec.copy()
    option_spec.update({
        "required": directives.flag,
        "optional": directives.flag,
    })

    def get_signature_prefix(self, sig: str) -> Sequence[Node]:
        """Return 'field' prefix for the signature."""
        return [addnodes.desc_sig_keyword("", "field"), addnodes.desc_sig_space()]

    def handle_signature(
        self, sig: str, signode: desc_signature
    ) -> tuple[str, str]:
        """Handle the field signature, adding [Required]/[Optional] markers."""
        fullname, prefix = super().handle_signature(sig, signode)

        if "required" in self.options:
            signode += addnodes.desc_sig_space()
            signode += addnodes.desc_annotation("", "[Required]")
        elif "optional" in self.options:
            signode += addnodes.desc_sig_space()
            signode += addnodes.desc_annotation("", "[Optional]")

        return fullname, prefix

    def get_index_text(self, modname: str, name_cls: tuple[str, str]) -> str:
        """Return the index text for this field."""
        name, cls = name_cls
        try:
            clsname, attrname = name.rsplit(".", 1)
            if modname and self.config.add_module_names:
                clsname = f"{modname}.{clsname}"
        except ValueError:
            if modname:
                return _("%s (in module %s)") % (name, modname)
            return name

        return _("%s (%s field)") % (attrname, clsname)
