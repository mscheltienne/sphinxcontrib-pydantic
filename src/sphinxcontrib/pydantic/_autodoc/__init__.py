"""Autodoc integration for Pydantic models."""

from sphinxcontrib.pydantic._autodoc._handlers import (
    PYDANTIC_SKIP_MEMBERS,
    autodoc_process_docstring,
    autodoc_skip_member,
    is_pydantic_internal,
    register_autodoc_handlers,
    should_skip_member,
)
