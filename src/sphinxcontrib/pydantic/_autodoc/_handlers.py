"""Autodoc event handlers for Pydantic models."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sphinx.util import logging

from sphinxcontrib.pydantic._inspection import (
    filter_mappings_by_field,
    get_field_info,
    get_model_info,
    get_validator_field_mappings,
    get_validator_info,
    is_pydantic_model,
    is_pydantic_settings,
)
from sphinxcontrib.pydantic._rendering import (
    create_role_reference,
    generate_field_summary_table,
    generate_root_type_line,
    generate_validator_summary_table,
)
from sphinxcontrib.pydantic._rendering._rst import (
    format_default_value,
    format_type_annotation,
)

if TYPE_CHECKING:
    from typing import Any

    from sphinx.application import Sphinx

_logger = logging.getLogger(__name__)

# Pydantic internal attributes that should be skipped in documentation
PYDANTIC_SKIP_MEMBERS: frozenset[str] = frozenset(
    {
        # Model class attributes
        "model_fields",
        "model_computed_fields",
        "model_config",
        "model_extra",
        "model_fields_set",
        # Private pydantic attributes
        "__pydantic_complete__",
        "__pydantic_core_schema__",
        "__pydantic_custom_init__",
        "__pydantic_decorators__",
        "__pydantic_extra__",
        "__pydantic_fields_set__",
        "__pydantic_generic_metadata__",
        "__pydantic_parent_namespace__",
        "__pydantic_post_init__",
        "__pydantic_private__",
        "__pydantic_root_model__",
        "__pydantic_serializer__",
        "__pydantic_validator__",
        # Class variables from pydantic
        "__class_vars__",
        "__private_attributes__",
        "__signature__",
        "__pydantic_fields__",
    }
)


def is_pydantic_internal(name: str) -> bool:
    """Check if a member name is a Pydantic internal attribute.

    Parameters
    ----------
    name : str
        The member name to check.

    Returns
    -------
    bool
        True if the name is a Pydantic internal attribute.
    """
    if name in PYDANTIC_SKIP_MEMBERS:
        return True
    # Also skip any __pydantic_* attributes not in the explicit list
    if name.startswith("__pydantic_"):
        return True
    return False


# Base classes whose methods should be skipped when documenting Pydantic models.
# Methods inherited from these classes have Markdown-style docstrings that are
# incompatible with Sphinx cross-references.
_PYDANTIC_BASE_CLASSES: tuple[str, ...] = ("BaseModel", "SQLModel")


def is_pydantic_base_member(obj: Any) -> bool:
    """Check if a member is inherited from a Pydantic/SQLModel base class.

    This checks the ``__qualname__`` attribute to determine if the member
    is defined on BaseModel, SQLModel, or their parent classes. Methods
    inherited from these base classes have Markdown-style docstrings that
    cause cross-reference warnings when processed by Sphinx.

    Parameters
    ----------
    obj : Any
        The member object to check.

    Returns
    -------
    bool
        True if the member is from a Pydantic/SQLModel base class.
    """
    # Get qualname, handling classmethods/staticmethods which wrap the function
    qualname = getattr(obj, "__qualname__", "")
    if hasattr(obj, "__func__"):  # classmethod/staticmethod wrapper
        qualname = getattr(obj.__func__, "__qualname__", "")

    # Check if defined on known Pydantic/SQLModel base classes
    for base in _PYDANTIC_BASE_CLASSES:
        if qualname.startswith(f"{base}."):
            return True

    return False


def should_skip_member(
    what: str,
    name: str,
    obj: Any,
    skip: bool,
    options: dict[str, Any],
) -> bool | None:
    """Determine if a member should be skipped in documentation.

    This is a helper function used by the autodoc-skip-member event handler.

    Parameters
    ----------
    what : str
        The type of the object (e.g., 'module', 'class', 'attribute').
    name : str
        The name of the member.
    obj : Any
        The member object.
    skip : bool
        Whether autodoc already decided to skip this member.
    options : dict[str, Any]
        The options given to the directive.

    Returns
    -------
    bool | None
        True to skip, False to include, None to use default behavior.
    """
    # Don't override if already decided to skip
    if skip:
        return None

    # Skip Pydantic internal attributes regardless of their documented type
    # (they can appear as 'attribute', 'class', or other types)
    if is_pydantic_internal(name):
        return True

    # Skip methods inherited from Pydantic/SQLModel base classes.
    # These have Markdown-style docstrings that cause cross-reference warnings.
    if is_pydantic_base_member(obj):
        return True

    return None


def autodoc_skip_member(
    app: Sphinx,
    what: str,
    name: str,
    obj: Any,
    skip: bool,
    options: dict[str, Any],
) -> bool | None:
    """Handle autodoc-skip-member event.

    This event handler skips Pydantic internal attributes and inherited
    BaseModel/SQLModel methods from documentation. Inherited methods are
    skipped because their docstrings use Markdown format which causes
    cross-reference warnings in Sphinx.

    Parameters
    ----------
    app : Sphinx
        The Sphinx application.
    what : str
        The type of the object.
    name : str
        The name of the member.
    obj : Any
        The member object.
    skip : bool
        Whether to skip this member.
    options : dict[str, Any]
        The options given to the directive.

    Returns
    -------
    bool | None
        True to skip, False to include, None to use default behavior.
    """
    return should_skip_member(what, name, obj, skip, options)


def autodoc_process_docstring(
    app: Sphinx,
    what: str,
    name: str,
    obj: Any,
    options: dict[str, Any],
    lines: list[str],
) -> None:
    """Handle autodoc-process-docstring event.

    This event handler adds Pydantic-specific documentation (field summaries,
    validator summaries) to class docstrings for Pydantic models, and
    "Validated by" sections to field attribute docstrings.

    Parameters
    ----------
    app : Sphinx
        The Sphinx application.
    what : str
        The type of the object.
    name : str
        The fully qualified name of the object.
    obj : Any
        The object itself.
    options : dict[str, Any]
        The options given to the directive.
    lines : list[str]
        The lines of the docstring (modified in place).
    """
    if what == "class":
        _process_class_docstring(app, name, obj, options, lines)
    elif what == "attribute":
        _process_attribute_docstring(app, name, obj, options, lines)


def _process_class_docstring(
    app: Sphinx,
    name: str,
    obj: Any,
    options: dict[str, Any],
    lines: list[str],
) -> None:
    """Process class docstring for Pydantic models."""
    # Only process Pydantic models
    if not is_pydantic_model(obj):
        return

    _logger.debug("Processing Pydantic model: %s", name)

    # Get model info
    try:
        model_info = get_model_info(obj)
    except Exception as e:
        _logger.warning("Failed to get model info for %s: %s", name, e)
        return

    # Add field summary if configured
    show_field_summary = getattr(
        app.config, "sphinxcontrib_pydantic_model_show_field_summary", True
    )
    if show_field_summary and model_info.field_names:
        _add_field_summary(obj, model_info, app, lines)

    # Add validator summary if configured
    show_validator_summary = getattr(
        app.config, "sphinxcontrib_pydantic_model_show_validator_summary", True
    )
    validators = list(model_info.validator_names) + list(
        model_info.model_validator_names
    )
    if show_validator_summary and validators:
        _add_validator_summary(obj, model_info, validators, app, lines)

    # Add detailed field documentation if configured
    show_field_doc = getattr(
        app.config, "sphinxcontrib_pydantic_model_show_field_doc", True
    )
    # Skip for RootModel (already displayed as "Root Type")
    is_root = model_info.is_root_model and len(model_info.field_names) == 1
    if show_field_doc and model_info.field_names and not is_root:
        field_doc_lines = _generate_field_documentation(obj, model_info, app)
        if field_doc_lines:
            lines.extend(field_doc_lines)


def _process_attribute_docstring(
    app: Sphinx,
    name: str,
    obj: Any,
    options: dict[str, Any],
    lines: list[str],
) -> None:
    """Process attribute docstring to add 'Validated by' section for fields."""
    # Parse the fully qualified name to get model path and field name
    parts = name.rsplit(".", 1)
    if len(parts) != 2:
        return

    model_path, field_name = parts

    # Try to import the model class
    try:
        module_parts = model_path.rsplit(".", 1)
        if len(module_parts) != 2:
            return
        module_name, class_name = module_parts
        module = __import__(module_name, fromlist=[class_name])
        model = getattr(module, class_name, None)
    except (ImportError, AttributeError):
        return

    if not is_pydantic_model(model):
        return

    # Check if this is actually a field
    if field_name not in model.model_fields:
        return

    # Get validators for this field
    mappings = get_validator_field_mappings(model)
    field_mappings = filter_mappings_by_field(mappings, field_name)

    if not field_mappings:
        return

    # Add "Validated by" section
    lines.append("")
    lines.append(":Validated by:")
    for mapping in sorted(field_mappings, key=lambda m: m.validator_name):
        ref = create_role_reference(mapping.validator_name, mapping.validator_ref)
        lines.append(f"   {ref}")


def _add_field_summary(
    model: type,
    model_info: Any,
    app: Sphinx,
    lines: list[str],
) -> None:
    """Add field summary table to docstring lines.

    For RootModel classes, this generates a cleaner "Root Type" line instead
    of a full field summary table with just a "root" entry.

    Parameters
    ----------
    model : type
        The Pydantic model class.
    model_info : ModelInfo
        Information about the model.
    app : Sphinx
        The Sphinx application.
    lines : list[str]
        The docstring lines to modify.
    """
    # Build model path for cross-references
    model_path = f"{model.__module__}.{model.__name__}"

    try:
        fields = [get_field_info(model, name) for name in model_info.field_names]

        # For RootModel, use a cleaner root type display
        if model_info.is_root_model and len(fields) == 1 and fields[0].name == "root":
            summary_lines = generate_root_type_line(fields[0])
        else:
            # Regular field summary table
            show_alias = getattr(
                app.config, "sphinxcontrib_pydantic_field_show_alias", True
            )
            show_default = getattr(
                app.config, "sphinxcontrib_pydantic_field_show_default", True
            )
            show_required = getattr(
                app.config, "sphinxcontrib_pydantic_field_show_required", True
            )
            show_constraints = getattr(
                app.config, "sphinxcontrib_pydantic_field_show_constraints", True
            )
            summary_lines = generate_field_summary_table(
                fields,
                model_path,
                show_alias=show_alias,
                show_default=show_default,
                show_required=show_required,
                show_constraints=show_constraints,
            )

        if summary_lines:
            lines.append("")
            lines.extend(summary_lines)
    except Exception as e:
        _logger.warning("Failed to generate field summary: %s", e)


def _add_validator_summary(
    model: type,
    model_info: Any,
    validator_names: list[str],
    app: Sphinx,
    lines: list[str],
) -> None:
    """Add validator summary table to docstring lines.

    Parameters
    ----------
    model : type
        The Pydantic model class.
    model_info : ModelInfo
        Information about the model.
    validator_names : list[str]
        Names of validators to include.
    app : Sphinx
        The Sphinx application.
    lines : list[str]
        The docstring lines to modify.
    """
    list_fields = getattr(
        app.config, "sphinxcontrib_pydantic_validator_list_fields", True
    )

    # Build model path for cross-references
    model_path = f"{model.__module__}.{model.__name__}"

    try:
        validators = [get_validator_info(model, name) for name in validator_names]
        summary_lines = generate_validator_summary_table(
            validators,
            model_path,
            list_fields=list_fields,
        )
        if summary_lines:
            lines.append("")
            lines.extend(summary_lines)
    except Exception as e:
        _logger.warning("Failed to generate validator summary: %s", e)


def _generate_field_documentation(
    model: type,
    model_info: Any,
    app: Sphinx,
) -> list[str]:
    """Generate detailed field documentation for a Pydantic model.

    Generates RST directives for each field with description,
    constraints, and validators.

    Parameters
    ----------
    model : type
        The Pydantic model class.
    model_info : ModelInfo
        Information about the model.
    app : Sphinx
        The Sphinx application.

    Returns
    -------
    list[str]
        RST lines for detailed field documentation.
    """
    lines: list[str] = []

    # Get validator mappings
    mappings = get_validator_field_mappings(model)

    for field_name in model_info.field_names:
        try:
            field = get_field_info(model, field_name)
        except Exception:
            continue

        # Generate field directive
        lines.append("")
        lines.append(f".. py:pydantic_field:: {field_name}")

        if field.is_required:
            lines.append("   :required:")
        else:
            lines.append("   :optional:")

        # Add type annotation
        type_str = format_type_annotation(field.annotation)
        lines.append(f"   :type: {type_str}")

        # Add default value
        if field.has_default:
            default_str = format_default_value(field.default)
            lines.append(f"   :value: {default_str}")
        elif field.has_default_factory:
            lines.append("   :value: *factory*")

        lines.append("")

        # Add field description
        if field.description:
            lines.append(f"   {field.description}")
            lines.append("")

        # Add constraints
        if field.constraints:
            lines.append("   :Constraints:")
            for key, value in field.constraints.items():
                lines.append(f"      - **{key}** = {value}")
            lines.append("")

        # Add validators
        field_mappings = filter_mappings_by_field(mappings, field_name)
        if field_mappings:
            lines.append("   :Validated by:")
            for mapping in sorted(field_mappings, key=lambda m: m.validator_name):
                ref = create_role_reference(
                    mapping.validator_name, mapping.validator_ref
                )
                lines.append(f"      {ref}")
            lines.append("")

    return lines


def autodoc_process_signature(
    app: Sphinx,
    what: str,
    name: str,
    obj: Any,
    options: dict[str, Any],
    signature: str | None,
    return_annotation: str | None,
) -> tuple[str | None, str | None] | None:
    """Handle autodoc-process-signature event.

    Hides parameter list for Pydantic models/settings when configured.
    This prevents cross-reference warnings for types without intersphinx
    inventories (annotated_types, pydantic_settings internals, etc.).

    Parameters
    ----------
    app : Sphinx
        The Sphinx application.
    what : str
        The type of the object (e.g., 'class', 'method').
    name : str
        The fully qualified name of the object.
    obj : Any
        The object itself.
    options : dict[str, Any]
        The options given to the directive.
    signature : str | None
        The signature string.
    return_annotation : str | None
        The return annotation string.

    Returns
    -------
    tuple[str | None, str | None] | None
        Modified (signature, return_annotation) or None to use defaults.
    """
    if what != "class" or not is_pydantic_model(obj):
        return None

    # Check if we should hide the parameter list
    if is_pydantic_settings(obj):
        hide = getattr(
            app.config, "sphinxcontrib_pydantic_settings_hide_paramlist", True
        )
    else:
        hide = getattr(app.config, "sphinxcontrib_pydantic_model_hide_paramlist", True)

    if hide:
        return ("", return_annotation)  # Empty signature

    return None  # Use default signature


def register_autodoc_handlers(app: Sphinx) -> None:
    """Register autodoc event handlers with Sphinx.

    Parameters
    ----------
    app : Sphinx
        The Sphinx application instance.
    """
    app.connect("autodoc-skip-member", autodoc_skip_member)
    app.connect("autodoc-process-docstring", autodoc_process_docstring)
    app.connect("autodoc-process-signature", autodoc_process_signature)
