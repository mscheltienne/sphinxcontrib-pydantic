"""Unit tests for the legacy autodoc_pydantic inventory interop."""

from __future__ import annotations

from types import SimpleNamespace

from sphinxcontrib.pydantic._compat import (
    _legacy_object_types,
    _register_legacy_object_types,
)


def _fake_app() -> SimpleNamespace:
    """Return a stub Sphinx app exposing only ``registry.domain_object_types``.

    Returns
    -------
    app : types.SimpleNamespace
        Stub with an empty ``registry.domain_object_types`` dict.
    """
    return SimpleNamespace(registry=SimpleNamespace(domain_object_types={}))


def _fake_config(*, enabled: bool) -> SimpleNamespace:
    """Return a stub config carrying the interop flag.

    Parameters
    ----------
    enabled : bool
        Value of ``sphinxcontrib_pydantic_resolve_legacy_inventories``.

    Returns
    -------
    config : types.SimpleNamespace
        Stub configuration.
    """
    return SimpleNamespace(sphinxcontrib_pydantic_resolve_legacy_inventories=enabled)


def test_legacy_object_types_mirror_autodoc_pydantic() -> None:
    """The five autodoc_pydantic object types are declared with matching roles."""
    types = _legacy_object_types()
    assert set(types) == {
        "pydantic_model",
        "pydantic_settings",
        "pydantic_field",
        "pydantic_validator",
        "pydantic_config",
    }
    # Class-like types must carry the ``class`` role so ``:py:class:`` resolves;
    # the others must not (they are not classes).
    for name in ("pydantic_model", "pydantic_settings"):
        assert "class" in types[name].roles
    for name in ("pydantic_field", "pydantic_validator", "pydantic_config"):
        assert "class" not in types[name].roles
    # Every type is referenceable by the generic ``obj`` role.
    assert all("obj" in objtype.roles for objtype in types.values())


def test_register_populates_py_domain_when_enabled() -> None:
    """Enabling the flag registers the object types on the py domain."""
    app = _fake_app()
    _register_legacy_object_types(app, _fake_config(enabled=True))

    registered = app.registry.domain_object_types["py"]
    assert registered.keys() == _legacy_object_types().keys()
    assert "class" in registered["pydantic_model"].roles


def test_register_is_noop_when_disabled() -> None:
    """The default (disabled) leaves the registry untouched."""
    app = _fake_app()
    _register_legacy_object_types(app, _fake_config(enabled=False))
    assert app.registry.domain_object_types == {}


def test_register_does_not_clobber_existing_object_type() -> None:
    """An existing registration (e.g. autodoc_pydantic) is preserved."""
    app = _fake_app()
    sentinel = object()
    app.registry.domain_object_types["py"] = {"pydantic_model": sentinel}

    _register_legacy_object_types(app, _fake_config(enabled=True))

    # Pre-existing entry kept; the remaining four still added.
    assert app.registry.domain_object_types["py"]["pydantic_model"] is sentinel
    assert "pydantic_settings" in app.registry.domain_object_types["py"]
