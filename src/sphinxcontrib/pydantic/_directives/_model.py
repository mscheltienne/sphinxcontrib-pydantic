"""Pydantic model documentation directive."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from docutils import nodes
from docutils.parsers.rst import directives
from docutils.statemachine import StringList
from sphinx import addnodes
from sphinx.util import logging
from sphinx.util.nodes import make_id

from sphinxcontrib.pydantic._directives._base import PydanticDirective, flag_or_value
from sphinxcontrib.pydantic._inspection import (
    FieldInfo,
    ValidatorInfo,
    filter_mappings_by_field,
    get_field_info,
    get_model_info,
    get_validator_field_mappings,
    get_validator_info,
    is_pydantic_model,
)
from sphinxcontrib.pydantic._rendering import (
    GeneratorConfig,
    config_from_directive,
    create_role_reference,
    format_type_annotation,
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

    #: Config prefix for looking up Sphinx config values ("model" or "settings")
    _config_prefix: ClassVar[str] = "model"

    option_spec: ClassVar[dict[str, Any]] = {
        # Inherited from base
        "module": directives.unchanged,
        "noindex": directives.flag,
        # Model-specific display options
        "show-json": flag_or_value,
        "show-field-summary": flag_or_value,
        "show-validator-summary": flag_or_value,
        "show-members": flag_or_value,
        # Field display options
        "show-alias": flag_or_value,
        "show-default": flag_or_value,
        "show-required": flag_or_value,
        "show-constraints": flag_or_value,
        # Validator display options
        "list-fields": flag_or_value,
        # Signature options
        "signature-prefix": directives.unchanged,
        "hide-paramlist": flag_or_value,
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
        # Create config from directive options with Sphinx config fallback
        config = config_from_directive(
            self.options, self.env.config, prefix=self._config_prefix
        )

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
        prefix = config.signature_prefix
        sig += addnodes.desc_annotation(prefix + " ", prefix + " ")
        sig += addnodes.desc_name(model_info.name, model_info.name)

        # Register the object with the Python domain for cross-referencing
        if "noindex" not in self.options:
            fullname = f"{model_info.module}.{model_info.name}"
            node_id = make_id(self.env, self.state.document, "", fullname)
            sig["ids"].append(node_id)
            self.state.document.note_explicit_target(sig)

            domain = self.env.domains.python_domain
            domain.note_object(fullname, "class", node_id, location=sig)

        desc += sig

        # Create the content
        content = addnodes.desc_content()

        # Add docstring
        if model_info.docstring:
            self._parse_docstring(model_info.docstring, content)

        # Compute model path for cross-references
        model_path = f"{model_info.module}.{model_info.name}"

        # Collect field and validator info for summary tables and detailed docs
        fields: list[FieldInfo] = []
        if model_info.field_names:
            fields = [get_field_info(model, name) for name in model_info.field_names]

        validators = list(model_info.validator_names) + list(
            model_info.model_validator_names
        )
        validator_infos: list[ValidatorInfo] = []
        if validators:
            validator_infos = [get_validator_info(model, name) for name in validators]

        # Add field summary table
        if config.show_field_summary and fields:
            self._add_field_summary(fields, model_path, config, content)

        # Add validator summary table
        if config.show_validator_summary and validator_infos:
            self._add_validator_summary(validator_infos, model_path, config, content)

        # Add JSON schema if requested
        if config.show_json:
            self._add_json_schema(model, content)

        # Add detailed field documentation (creates cross-reference targets)
        if config.show_members and fields:
            self._generate_field_docs(fields, model, model_path, config, content)

        # Add detailed validator documentation (creates cross-reference targets)
        if config.show_members and validator_infos:
            self._generate_validator_docs(validator_infos, model_path, content)

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
        model_path: str,
        config: GeneratorConfig,
        parent: nodes.Element,
    ) -> None:
        """Add a field summary table to the parent node.

        Parameters
        ----------
        fields : list[FieldInfo]
            The fields to summarize.
        model_path : str
            The fully qualified path to the model (e.g., ``module.ClassName``).
        config : GeneratorConfig
            The generator configuration.
        parent : nodes.Element
            The parent node to add content to.
        """
        lines = generate_field_summary_table(
            fields,
            model_path,
            show_alias=config.field_show_alias,
            show_default=config.field_show_default,
            show_required=config.field_show_required,
            show_constraints=config.field_show_constraints,
        )

        if lines:
            string_list = StringList(lines)
            self.state.nested_parse(string_list, 0, parent)

    def _add_validator_summary(
        self,
        validators: list[ValidatorInfo],
        model_path: str,
        config: GeneratorConfig,
        parent: nodes.Element,
    ) -> None:
        """Add a validator summary table to the parent node.

        Parameters
        ----------
        validators : list[ValidatorInfo]
            The validators to summarize.
        model_path : str
            The fully qualified path to the model (e.g., ``module.ClassName``).
        config : GeneratorConfig
            The generator configuration.
        parent : nodes.Element
            The parent node to add content to.
        """
        lines = generate_validator_summary_table(
            validators,
            model_path,
            list_fields=config.validator_list_fields,
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

    def _generate_field_docs(
        self,
        fields: list[FieldInfo],
        model: type[BaseModel],
        model_path: str,
        config: GeneratorConfig,
        parent: nodes.Element,
    ) -> None:
        """Generate detailed documentation for each field.

        Creates individual field entries that serve as cross-reference targets
        for the summary table links.

        Parameters
        ----------
        fields : list[FieldInfo]
            The fields to document.
        model : type[BaseModel]
            The Pydantic model class.
        model_path : str
            The fully qualified path to the model (e.g., ``module.ClassName``).
        config : GeneratorConfig
            The generator configuration.
        parent : nodes.Element
            The parent node to add content to.
        """
        # Get validator-field mappings for "Validated by" sections
        mappings = get_validator_field_mappings(model)

        for field in sorted(fields, key=lambda f: f.name):
            # Create the field desc node
            field_desc = addnodes.desc()
            field_desc["domain"] = "py"
            field_desc["objtype"] = "attribute"
            field_desc["noindex"] = "noindex" in self.options

            # Create the signature
            sig = addnodes.desc_signature()
            sig["module"] = model_path.rsplit(".", 1)[0] if "." in model_path else ""
            sig["class"] = model_path.rsplit(".", 1)[-1]
            sig["fullname"] = f"{model_path.rsplit('.', 1)[-1]}.{field.name}"

            # Add "field" prefix
            sig += addnodes.desc_sig_keyword("", "field")
            sig += addnodes.desc_sig_space()

            # Add field name
            sig += addnodes.desc_name(field.name, field.name)

            # Add type annotation
            if field.annotation is not None:
                sig += addnodes.desc_sig_punctuation("", ":")
                sig += addnodes.desc_sig_space()
                type_str = format_type_annotation(field.annotation, as_rst=False)
                sig += addnodes.desc_sig_name("", type_str)

            # Add [Required] or [Optional] marker
            sig += addnodes.desc_sig_space()
            if field.is_required:
                sig += addnodes.desc_annotation("", "[Required]")
            else:
                sig += addnodes.desc_annotation("", "[Optional]")

            # Register the field with Python domain for cross-referencing
            if "noindex" not in self.options:
                fullname = f"{model_path}.{field.name}"
                node_id = make_id(self.env, self.state.document, "", fullname)
                sig["ids"].append(node_id)
                self.state.document.note_explicit_target(sig)

                domain = self.env.domains.python_domain
                domain.note_object(fullname, "attribute", node_id, location=sig)

            field_desc += sig

            # Create the content
            field_content = addnodes.desc_content()

            # Build RST content for the field
            content_lines: list[str] = []

            # Add description
            if field.description:
                content_lines.append(field.description)
                content_lines.append("")

            # Add constraints section
            if config.field_show_constraints and field.constraints:
                content_lines.append(":Constraints:")
                for key, value in field.constraints.items():
                    content_lines.append(f"   - **{key}** = ``{value}``")
                content_lines.append("")

            # Add "Validated by" section
            field_mappings = filter_mappings_by_field(mappings, field.name)
            if field_mappings:
                content_lines.append(":Validated by:")
                for mapping in sorted(field_mappings, key=lambda m: m.validator_name):
                    ref = create_role_reference(
                        mapping.validator_name, mapping.validator_ref
                    )
                    content_lines.append(f"   {ref}")
                content_lines.append("")

            # Parse the content lines into nodes
            if content_lines:
                string_list = StringList(content_lines)
                self.state.nested_parse(string_list, 0, field_content)

            field_desc += field_content
            parent += field_desc

    def _generate_validator_docs(
        self,
        validators: list[ValidatorInfo],
        model_path: str,
        parent: nodes.Element,
    ) -> None:
        """Generate detailed documentation for each validator.

        Creates individual validator entries that serve as cross-reference targets
        for the summary table links.

        Parameters
        ----------
        validators : list[ValidatorInfo]
            The validators to document.
        model_path : str
            The fully qualified path to the model (e.g., ``module.ClassName``).
        parent : nodes.Element
            The parent node to add content to.
        """
        for validator in sorted(validators, key=lambda v: v.name):
            # Create the validator desc node
            validator_desc = addnodes.desc()
            validator_desc["domain"] = "py"
            validator_desc["objtype"] = "method"
            validator_desc["noindex"] = "noindex" in self.options

            # Create the signature
            sig = addnodes.desc_signature()
            sig["module"] = model_path.rsplit(".", 1)[0] if "." in model_path else ""
            sig["class"] = model_path.rsplit(".", 1)[-1]
            sig["fullname"] = f"{model_path.rsplit('.', 1)[-1]}.{validator.name}"

            # Add "validator" prefix
            sig += addnodes.desc_sig_keyword("", "validator")
            sig += addnodes.desc_sig_space()

            # Add validator name
            sig += addnodes.desc_name(validator.name, validator.name)

            # Add mode in parentheses
            sig += addnodes.desc_sig_punctuation("", "(")
            sig += addnodes.desc_sig_name("", f"mode={validator.mode}")
            sig += addnodes.desc_sig_punctuation("", ")")

            # Register the validator with Python domain for cross-referencing
            if "noindex" not in self.options:
                fullname = f"{validator.defining_class_path}.{validator.name}"
                node_id = make_id(self.env, self.state.document, "", fullname)
                sig["ids"].append(node_id)
                self.state.document.note_explicit_target(sig)

                domain = self.env.domains.python_domain
                domain.note_object(fullname, "method", node_id, location=sig)

            validator_desc += sig

            # Create the content
            validator_content = addnodes.desc_content()

            # Build RST content for the validator
            content_lines: list[str] = []

            # Add docstring
            if validator.docstring:
                content_lines.append(validator.docstring)
                content_lines.append("")

            # Add fields section for field validators
            if validator.fields and not validator.is_model_validator:
                content_lines.append(":Validates:")
                for field_name in validator.fields:
                    if field_name == "*":
                        content_lines.append("   all fields")
                    else:
                        field_path = validator.field_class_paths.get(
                            field_name, model_path
                        )
                        ref = create_role_reference(
                            field_name, f"{field_path}.{field_name}"
                        )
                        content_lines.append(f"   {ref}")
                content_lines.append("")
            elif validator.is_model_validator:
                content_lines.append(":Validates: entire model")
                content_lines.append("")

            # Parse the content lines into nodes
            if content_lines:
                string_list = StringList(content_lines)
                self.state.nested_parse(string_list, 0, validator_content)

            validator_desc += validator_content
            parent += validator_desc


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
