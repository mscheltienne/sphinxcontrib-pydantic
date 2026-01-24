"""Pytest configuration and fixtures for sphinxcontrib-pydantic tests."""

from __future__ import annotations

import sys
from collections.abc import Callable, Iterator
from io import StringIO
from pathlib import Path

import pytest
from bs4 import BeautifulSoup
from sphinx.testing.util import SphinxTestApp

# Add tests directory to path so assets can be imported
TESTS_DIR = Path(__file__).parent
ASSETS_DIR = TESTS_DIR / "assets"
sys.path.insert(0, str(TESTS_DIR))


def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest options."""
    # Register custom markers
    config.addinivalue_line(
        "markers",
        "sphinx(buildername, testroot, confoverrides, ...): "
        "arguments to initialize the sphinx test application.",
    )


@pytest.fixture(scope="session")
def rootdir() -> Path:
    """Path to test roots directory."""
    return ASSETS_DIR


@pytest.fixture(scope="session")
def assets_dir() -> Path:
    """Path to test assets directory."""
    return ASSETS_DIR


@pytest.fixture
def make_app(
    tmp_path: Path,
    rootdir: Path,
) -> Iterator[Callable[..., SphinxTestApp]]:
    """Create test Sphinx applications.

    This fixture creates SphinxTestApp instances for testing. It handles
    cleanup automatically after each test.

    Yields
    ------
    Callable[..., SphinxTestApp]
        Factory function to create SphinxTestApp instances.
    """
    apps: list[SphinxTestApp] = []
    saved_path = sys.path.copy()

    def _make_app(
        buildername: str = "html",
        srcdir: Path | None = None,
        confoverrides: dict | None = None,
        freshenv: bool = True,
        **kwargs,
    ) -> SphinxTestApp:
        if srcdir is None:
            srcdir = tmp_path / "src"
            srcdir.mkdir(exist_ok=True)
            # Copy minimal conf.py and index.rst
            (srcdir / "conf.py").write_text(
                'extensions = ["sphinx.ext.autodoc", "sphinxcontrib.pydantic"]\n'
                'project = "Test"\n'
                'exclude_patterns = ["_build"]\n'
            )
            (srcdir / "index.rst").write_text("Test\n====\n")

        status = StringIO()
        warning = StringIO()

        confoverrides = confoverrides or {}

        app = SphinxTestApp(
            buildername=buildername,
            srcdir=srcdir,
            freshenv=freshenv,
            confoverrides=confoverrides,
            status=status,
            warning=warning,
            **kwargs,
        )
        apps.append(app)
        return app

    yield _make_app

    # Cleanup
    sys.path[:] = saved_path
    for app in reversed(apps):
        app.cleanup()


@pytest.fixture
def app(make_app: Callable[..., SphinxTestApp]) -> SphinxTestApp:
    """Provide a basic Sphinx test application."""
    return make_app()


@pytest.fixture
def parse_html() -> Callable[[str], BeautifulSoup]:
    """Fixture to parse HTML content.

    Returns
    -------
    Callable[[str], BeautifulSoup]
        Function that parses HTML string into BeautifulSoup object.
    """

    def _parse(html: str) -> BeautifulSoup:
        return BeautifulSoup(html, "html.parser")

    return _parse
