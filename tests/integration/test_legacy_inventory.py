"""Integration tests for resolving legacy ``autodoc_pydantic`` inventories."""

from __future__ import annotations

import zlib
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

    from bs4 import BeautifulSoup
    from sphinx.testing.util import SphinxTestApp


def _write_legacy_inventory(path: Path) -> None:
    """Write a minimal Sphinx v2 ``objects.inv`` in autodoc_pydantic's style.

    The model is published under the custom ``py:pydantic_model`` object type
    (and a field under ``py:pydantic_field``), exactly as ``autodoc_pydantic``
    would, rather than the stock ``py:class`` / ``py:attribute``.

    Parameters
    ----------
    path : pathlib.Path
        Destination of the inventory file.
    """
    entries = (
        "legacy_pkg.LegacyModel py:pydantic_model 1 legacymodel.html#$ -\n"
        "legacy_pkg.LegacyModel.value py:pydantic_field 1 legacymodel.html#$ -\n"
    )
    header = (
        b"# Sphinx inventory version 2\n"
        b"# Project: legacy\n"
        b"# Version: 1.0\n"
        b"# The remainder of this file is compressed using zlib.\n"
    )
    path.write_bytes(header + zlib.compress(entries.encode("utf-8")))


def _build(
    make_app: Callable[..., SphinxTestApp],
    tmp_path: Path,
    *,
    resolve_legacy: bool,
) -> SphinxTestApp:
    """Build a project that cross-references a legacy inventory.

    Parameters
    ----------
    make_app : callable
        The ``make_app`` fixture factory.
    tmp_path : pathlib.Path
        Per-test temporary directory.
    resolve_legacy : bool
        Value of ``sphinxcontrib_pydantic_resolve_legacy_inventories``.

    Returns
    -------
    app : sphinx.testing.util.SphinxTestApp
        The built application.
    """
    inv = tmp_path / "legacy.inv"
    _write_legacy_inventory(inv)

    srcdir = tmp_path / "src"
    srcdir.mkdir()
    (srcdir / "conf.py").write_text(
        'extensions = ["sphinx.ext.autodoc", "sphinx.ext.intersphinx", '
        '"sphinxcontrib.pydantic"]\n'
        'project = "Test"\n'
        'exclude_patterns = ["_build"]\n'
        f'intersphinx_mapping = {{"legacy": ("https://legacy.example/", '
        f"r\"{inv}\")}}\n"
        f"sphinxcontrib_pydantic_resolve_legacy_inventories = {resolve_legacy}\n"
    )
    (srcdir / "index.rst").write_text(
        "Test Project\n"
        "============\n"
        "\n"
        "Model ref: :py:obj:`legacy_pkg.LegacyModel`\n"
        "\n"
        "Class ref: :py:class:`legacy_pkg.LegacyModel`\n"
    )

    app = make_app(srcdir=srcdir)
    app.build()
    return app


def _legacy_links(soup: BeautifulSoup) -> list[str]:
    """Return hrefs of external links pointing at the legacy inventory.

    Parameters
    ----------
    soup : bs4.BeautifulSoup
        Parsed ``index.html``.

    Returns
    -------
    hrefs : list of str
        Hrefs resolving to the legacy model page.
    """
    return [
        link.get("href", "")
        for link in soup.select("a.reference.external")
        if "legacymodel.html" in link.get("href", "")
    ]


def test_legacy_inventory_resolves_when_enabled(
    make_app: Callable[..., SphinxTestApp],
    tmp_path: Path,
    parse_html: Callable[[str], BeautifulSoup],
) -> None:
    """``py:obj`` / ``py:class`` refs to a ``py:pydantic_model`` entry resolve."""
    app = _build(make_app, tmp_path, resolve_legacy=True)
    assert app.statuscode == 0

    html = (Path(app.outdir) / "index.html").read_text(encoding="utf-8")
    soup = parse_html(html)
    hrefs = _legacy_links(soup)
    # Both the :py:obj: and the :py:class: reference must resolve to the model.
    assert len(hrefs) == 2, f"expected 2 resolved legacy links, found: {hrefs}"
    assert all(h.startswith("https://legacy.example/legacymodel.html") for h in hrefs)


def test_legacy_inventory_not_resolved_by_default(
    make_app: Callable[..., SphinxTestApp],
    tmp_path: Path,
    parse_html: Callable[[str], BeautifulSoup],
) -> None:
    """Without the opt-in, a ``py:pydantic_model`` ref stays unresolved text."""
    app = _build(make_app, tmp_path, resolve_legacy=False)
    assert app.statuscode == 0

    html = (Path(app.outdir) / "index.html").read_text(encoding="utf-8")
    soup = parse_html(html)
    assert _legacy_links(soup) == []
    # The reference text is still rendered, just not hyperlinked.
    assert "legacy_pkg.LegacyModel" in soup.get_text()
