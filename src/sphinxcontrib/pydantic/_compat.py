"""Interoperate with inventories produced by ``autodoc_pydantic``.

``autodoc_pydantic`` -- the unmaintained predecessor of this extension,
incompatible with Sphinx 9+ -- documents Pydantic objects under custom
Python-domain object types (``pydantic_model``, ``pydantic_settings``,
``pydantic_field``, ``pydantic_validator`` and ``pydantic_config``). A project
documented with it therefore publishes ``objects.inv`` entries such as
``py:pydantic_model pkg.Model`` rather than the stock ``py:class``.

This extension documents models as plain ``py:class`` and never teaches the
Python domain about those object types, so a cross-reference into such a legacy
inventory (e.g. through intersphinx) cannot resolve and a ``nitpicky`` build
fails. When ``sphinxcontrib_pydantic_resolve_legacy_inventories`` is enabled,
this module registers those object types -- object types only, no directives --
so intersphinx maps the legacy inventory entries back to the stock ``obj`` /
``class`` roles and the references resolve.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sphinx.domains import ObjType

if TYPE_CHECKING:
    from sphinx.application import Sphinx
    from sphinx.config import Config


def _legacy_object_types() -> dict[str, ObjType]:
    """Return the object types ``autodoc_pydantic`` registers in the py domain.

    Returns
    -------
    object_types : dict of str to sphinx.domains.ObjType
        Mapping mirroring ``autodoc_pydantic``'s ``OBJ_TYPES_MAPPING``. The
        class-like ``model`` / ``settings`` types carry the ``class`` role in
        addition to ``obj`` / ``any``; ``field`` / ``validator`` / ``config`` do
        not, matching how ``autodoc_pydantic`` declares them.
    """
    return {
        "pydantic_model": ObjType("model", "obj", "any", "class"),
        "pydantic_settings": ObjType("settings", "obj", "any", "class"),
        "pydantic_field": ObjType("field", "obj", "any"),
        "pydantic_validator": ObjType("validator", "obj", "any"),
        "pydantic_config": ObjType("config", "obj", "any"),
    }


def _register_legacy_object_types(app: Sphinx, config: Config) -> None:
    """Register ``autodoc_pydantic`` object types when interop is enabled.

    Connected to ``config-inited`` so the config value is available and the
    registration happens before the build environment instantiates the Python
    domain (which is what reads ``registry.domain_object_types``).

    Parameters
    ----------
    app : sphinx.application.Sphinx
        The Sphinx application instance.
    config : sphinx.config.Config
        The initialised build configuration.
    """
    if not config.sphinxcontrib_pydantic_resolve_legacy_inventories:
        return
    # ``Sphinx.add_object_type`` only targets the ``std`` domain, so register on
    # the registry directly, as ``autodoc_pydantic`` does. ``create_domains``
    # feeds these through ``Domain.add_object_type`` when the environment is set
    # up. ``pydantic_field`` is also registered as a *directive* by this
    # extension, but directives and object types live in separate registries, so
    # there is no collision (``autodoc_pydantic`` reuses the same names too).
    # ``setdefault`` avoids clobbering a real registration if ``autodoc_pydantic``
    # is loaded at the same time during a migration.
    object_types = app.registry.domain_object_types.setdefault("py", {})
    for name, objtype in _legacy_object_types().items():
        object_types.setdefault(name, objtype)


def register_compat(app: Sphinx) -> None:
    """Connect the legacy-inventory interop hook.

    Parameters
    ----------
    app : sphinx.application.Sphinx
        The Sphinx application instance.
    """
    app.connect("config-inited", _register_legacy_object_types)
