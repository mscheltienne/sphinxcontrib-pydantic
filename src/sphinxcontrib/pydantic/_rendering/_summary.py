"""Summary table generation for Pydantic models."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sphinxcontrib.pydantic._rendering._rst import (
    format_default_value,
    format_type_annotation,
)
from sphinxcontrib.pydantic._rendering._xref import create_role_reference

if TYPE_CHECKING:
    from sphinxcontrib.pydantic._inspection import FieldInfo, ValidatorInfo


def generate_field_summary_table(
    fields: list[FieldInfo],
    *,
    show_alias: bool = True,
    show_default: bool = True,
    show_required: bool = True,
    show_constraints: bool = True,
) -> list[str]:
    """Generate a field summary table in RST format.

    Parameters
    ----------
    fields : list[FieldInfo]
        The fields to include in the summary.
    show_alias : bool
        Whether to show field aliases.
    show_default : bool
        Whether to show default values.
    show_required : bool
        Whether to show required indicators.
    show_constraints : bool
        Whether to show constraints.

    Returns
    -------
    list[str]
        RST lines for the field summary table.
    """
    if not fields:
        return []

    lines: list[str] = []

    # Determine which columns to include
    columns = ["Field", "Type"]
    if show_required:
        columns.append("Required")
    if show_default:
        columns.append("Default")
    if show_alias and any(f.alias for f in fields):
        columns.append("Alias")
    if show_constraints and any(f.constraints for f in fields):
        columns.append("Constraints")

    # Build header
    lines.append("")
    lines.append(".. list-table:: Fields")
    lines.append("   :header-rows: 1")
    lines.append("   :widths: auto")
    lines.append("")

    # Header row
    lines.append("   * - " + columns[0])
    lines.extend("     - " + col for col in columns[1:])

    # Data rows
    for field in fields:
        row_data = _get_field_row_data(field, columns)
        lines.append("   * - " + row_data[0])
        lines.extend("     - " + cell for cell in row_data[1:])

    lines.append("")
    return lines


def _get_field_row_data(field: FieldInfo, columns: list[str]) -> list[str]:
    """Get the data for a single field row.

    Parameters
    ----------
    field : FieldInfo
        The field information.
    columns : list[str]
        The columns to include.

    Returns
    -------
    list[str]
        The cell values for the row.
    """
    row: list[str] = []

    for col in columns:
        if col == "Field":
            row.append(f"``{field.name}``")
        elif col == "Type":
            type_str = format_type_annotation(field.annotation)
            row.append(f"``{type_str}``")
        elif col == "Required":
            row.append("Yes" if field.is_required else "No")
        elif col == "Default":
            if field.has_default:
                default_str = format_default_value(field.default)
                row.append(f"``{default_str}``")
            elif field.has_default_factory:
                row.append("*factory*")
            else:
                row.append("")
        elif col == "Alias":
            row.append(f"``{field.alias}``" if field.alias else "")
        elif col == "Constraints":
            row.append(
                _format_constraints(field.constraints) if field.constraints else ""
            )

    return row


def _format_constraints(constraints: dict) -> str:
    """Format field constraints for display.

    Parameters
    ----------
    constraints : dict
        The constraints dictionary.

    Returns
    -------
    str
        Formatted constraints string.
    """
    parts = []
    for key, value in constraints.items():
        if key == "pattern":
            parts.append(f"pattern=``{value}``")
        else:
            parts.append(f"{key}={value}")
    return ", ".join(parts)


def generate_validator_summary_table(
    validators: list[ValidatorInfo],
    *,
    list_fields: bool = True,
    model_path: str | None = None,
) -> list[str]:
    """Generate a validator summary table in RST format.

    Parameters
    ----------
    validators : list[ValidatorInfo]
        The validators to include in the summary.
    list_fields : bool
        Whether to list validated fields.
    model_path : str | None
        The fully qualified model path (e.g., "module.Class"). If provided,
        cross-references will be generated for validators and fields.

    Returns
    -------
    list[str]
        RST lines for the validator summary table.
    """
    if not validators:
        return []

    lines: list[str] = []

    # Determine columns
    columns = ["Validator", "Mode"]
    if list_fields:
        columns.append("Fields")

    # Build header
    lines.append("")
    lines.append(".. list-table:: Validators")
    lines.append("   :header-rows: 1")
    lines.append("   :widths: auto")
    lines.append("")

    # Header row
    lines.append("   * - " + columns[0])
    lines.extend("     - " + col for col in columns[1:])

    # Data rows
    for validator in validators:
        row_data = _get_validator_row_data(validator, columns, model_path)
        lines.append("   * - " + row_data[0])
        lines.extend("     - " + cell for cell in row_data[1:])

    lines.append("")
    return lines


def _get_validator_row_data(
    validator: ValidatorInfo,
    columns: list[str],
    model_path: str | None = None,
) -> list[str]:
    """Get the data for a single validator row.

    Parameters
    ----------
    validator : ValidatorInfo
        The validator information.
    columns : list[str]
        The columns to include.
    model_path : str | None
        The fully qualified model path for cross-references.

    Returns
    -------
    list[str]
        The cell values for the row.
    """
    row: list[str] = []

    for col in columns:
        if col == "Validator":
            if model_path:
                ref = f"{model_path}.{validator.name}"
                row.append(create_role_reference(validator.name, ref))
            else:
                row.append(f"``{validator.name}``")
        elif col == "Mode":
            row.append(validator.mode)
        elif col == "Fields":
            if validator.is_model_validator:
                row.append("*model*")
            elif validator.fields:
                if model_path:
                    field_refs = [
                        create_role_reference(f, f"{model_path}.{f}")
                        for f in validator.fields
                    ]
                    row.append(", ".join(field_refs))
                else:
                    fields_str = ", ".join(f"``{f}``" for f in validator.fields)
                    row.append(fields_str)
            else:
                row.append("")

    return row
