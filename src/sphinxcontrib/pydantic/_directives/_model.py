"""Pydantic model documentation directive."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from docutils import nodes
from docutils.parsers.rst import directives
from docutils.statemachine import StringList
from sphinx import addnodes
from sphinx.util import logging

from sphinxcontrib.pydantic._directives._base import PydanticDirective, flag_or_value
from sphinxcontrib.pydantic._inspection import (
    FieldInfo,
    ValidatorInfo,
    get_field_info,
    get_model_info,
    get_validator_info,
    is_pydantic_model,
)
from sphinxcontrib.pydantic._rendering import (
    generate_field_summary_table,
    generate_validator_summary_table,
)

if TYPE_CHECKING:
    from typing import Any

    from sphinx.application import Sphinx

    from pydantic import BaseModel

_logger = logging.getLogger(__name__)


class PydanticModelDirective(PydanticDirective):
    """Directive for documenting a Pydantic model.

    Usage::

        .. pydantic-model:: mymodule.MyModel
           :show-json:
           :show-field-summary:
           :show-validator-summary:

    Or with explicit module::

        .. pydantic-model:: MyModel
           :module: mymodule
    """

    option_spec: ClassVar[dict[str, Any]] = {
        # Inherited from base
        "module": directives.unchanged,
        "noindex": directives.flag,
        # Model-specific options
        "show-json": flag_or_value,
        "show-field-summary": flag_or_value,
        "show-validator-summary": flag_or_value,
        "show-config": flag_or_value,
        # Member options
        "members": directives.unchanged,
        "inherited-members": directives.unchanged,
        "undoc-members": directives.flag,
    }

    def run(self) -> list[nodes.Node]:
        """Run the directive and generate documentation nodes.

        Returns
        -------
        list[nodes.Node]
            List of docutils nodes representing the model documentation.
        """
        # Get the model class
        objpath = self.get_object_path()
        model = self._import_model(objpath)

        if model is None:
            return [
                self.state.document.reporter.warning(
                    f"Cannot find Pydantic model: {objpath}",
                    line=self.lineno,
                )
            ]

        if not is_pydantic_model(model):
            return [
                self.state.document.reporter.warning(
                    f"Object is not a Pydantic model: {objpath}",
                    line=self.lineno,
                )
            ]

        # Get model info
        model_info = get_model_info(model)

        # Generate the documentation
        return self._generate_model_docs(model, model_info)

    def _import_model(self, objpath: str) -> type[BaseModel] | None:
        """Import a model class from its path.

        Parameters
        ----------
        objpath : str
            The fully qualified object path.

        Returns
        -------
        type[BaseModel] | None
            The model class, or None if not found.
        """
        try:
            parts = objpath.rsplit(".", 1)
            if len(parts) == 1:
                # No module specified, try current module context
                _logger.warning("No module specified for model: %s", objpath)
                return None

            module_path, class_name = parts
            module = __import__(module_path, fromlist=[class_name])
            return getattr(module, class_name, None)
        except (ImportError, AttributeError) as e:
            _logger.debug("Failed to import model %s: %s", objpath, e)
            return None

    def _generate_model_docs(
        self,
        model: type[BaseModel],
        model_info: Any,
    ) -> list[nodes.Node]:
        """Generate documentation nodes for a model.

        Parameters
        ----------
        model : type[BaseModel]
            The Pydantic model class.
        model_info : ModelInfo
            Information about the model.

        Returns
        -------
        list[nodes.Node]
            List of docutils nodes.
        """
        result: list[nodes.Node] = []

        # Create the main description node
        desc = addnodes.desc()
        desc["domain"] = "py"
        desc["objtype"] = "class"
        desc["noindex"] = "noindex" in self.options

        # Create the signature
        sig = addnodes.desc_signature()
        sig["module"] = model_info.module
        sig["class"] = ""
        sig["fullname"] = model_info.name

        # Add signature prefix
        prefix = self.get_option_or_config(
            "signature-prefix",
            "model_signature_prefix",
            "model",
        )
        sig += addnodes.desc_annotation(prefix + " ", prefix + " ")
        sig += addnodes.desc_name(model_info.name, model_info.name)

        desc += sig

        # Create the content
        content = addnodes.desc_content()

        # Add docstring
        if model_info.docstring:
            self._parse_docstring(model_info.docstring, content)

        # Add field summary table
        show_field_summary = self.get_option_or_config(
            "show-field-summary",
            "model_show_field_summary",
            True,
        )
        if show_field_summary and model_info.field_names:
            fields = [get_field_info(model, name) for name in model_info.field_names]
            self._add_field_summary(fields, content)

        # Add validator summary table
        show_validator_summary = self.get_option_or_config(
            "show-validator-summary",
            "model_show_validator_summary",
            True,
        )
        validators = list(model_info.validator_names) + list(
            model_info.model_validator_names
        )
        if show_validator_summary and validators:
            validator_infos = [get_validator_info(model, name) for name in validators]
            self._add_validator_summary(validator_infos, content)

        # Add JSON schema if requested
        show_json = self.get_option_or_config(
            "show-json",
            "model_show_json",
            False,
        )
        if show_json:
            self._add_json_schema(model, content)

        desc += content
        result.append(desc)

        return result

    def _parse_docstring(
        self,
        docstring: str,
        parent: nodes.Element,
    ) -> None:
        """Parse a docstring and add it to the parent node.

        Parameters
        ----------
        docstring : str
            The docstring text.
        parent : nodes.Element
            The parent node to add content to.
        """
        # Create a paragraph for the docstring
        lines = docstring.strip().split("\n")
        string_list = StringList(lines)
        self.state.nested_parse(string_list, 0, parent)

    def _add_field_summary(
        self,
        fields: list[FieldInfo],
        parent: nodes.Element,
    ) -> None:
        """Add a field summary table to the parent node.

        Parameters
        ----------
        fields : list[FieldInfo]
            The fields to summarize.
        parent : nodes.Element
            The parent node to add content to.
        """
        show_alias = self.get_option_or_config(
            "show-alias",
            "field_show_alias",
            True,
        )
        show_default = self.get_option_or_config(
            "show-default",
            "field_show_default",
            True,
        )
        show_required = self.get_option_or_config(
            "show-required",
            "field_show_required",
            True,
        )
        show_constraints = self.get_option_or_config(
            "show-constraints",
            "field_show_constraints",
            True,
        )

        lines = generate_field_summary_table(
            fields,
            show_alias=show_alias,
            show_default=show_default,
            show_required=show_required,
            show_constraints=show_constraints,
        )

        if lines:
            string_list = StringList(lines)
            self.state.nested_parse(string_list, 0, parent)

    def _add_validator_summary(
        self,
        validators: list[ValidatorInfo],
        parent: nodes.Element,
    ) -> None:
        """Add a validator summary table to the parent node.

        Parameters
        ----------
        validators : list[ValidatorInfo]
            The validators to summarize.
        parent : nodes.Element
            The parent node to add content to.
        """
        list_fields = self.get_option_or_config(
            "list-fields",
            "validator_list_fields",
            True,
        )

        lines = generate_validator_summary_table(
            validators,
            list_fields=list_fields,
        )

        if lines:
            string_list = StringList(lines)
            self.state.nested_parse(string_list, 0, parent)

    def _add_json_schema(
        self,
        model: type[BaseModel],
        parent: nodes.Element,
    ) -> None:
        """Add JSON schema to the parent node.

        Parameters
        ----------
        model : type[BaseModel]
            The Pydantic model.
        parent : nodes.Element
            The parent node to add content to.
        """
        import json

        try:
            schema = model.model_json_schema()
            schema_str = json.dumps(schema, indent=2)

            # Create a code block
            literal = nodes.literal_block(schema_str, schema_str)
            literal["language"] = "json"
            parent += literal
        except Exception as e:
            _logger.warning("Failed to generate JSON schema: %s", e)


class AutoPydanticModelDirective(PydanticModelDirective):
    """Auto-documenting directive for Pydantic models.

    This directive automatically imports and documents a Pydantic model,
    similar to autodoc's ``autoclass`` directive.

    Usage::

        .. autopydantic-model:: mymodule.MyModel
           :members:
           :show-field-summary:
    """


def register_directives(app: Sphinx) -> None:
    """Register model directives with Sphinx.

    Parameters
    ----------
    app : Sphinx
        The Sphinx application instance.
    """
    app.add_directive("pydantic-model", PydanticModelDirective)
    app.add_directive("autopydantic-model", AutoPydanticModelDirective)
