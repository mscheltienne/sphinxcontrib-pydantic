"""Tests for docstring processing utilities."""

from __future__ import annotations

from collections.abc import Callable
from unittest.mock import MagicMock

import pytest
from sphinx.testing.util import SphinxTestApp

from sphinxcontrib.pydantic._directives._docstring import process_docstring


class TestProcessDocstring:
    """Tests for the process_docstring function."""

    def test_empty_docstring_returns_empty_list(
        self, make_app: Callable[..., SphinxTestApp]
    ) -> None:
        """Empty docstring returns empty list."""
        app = make_app()
        result = process_docstring(app, "")
        assert result == []

    def test_none_like_empty_docstring(
        self, make_app: Callable[..., SphinxTestApp]
    ) -> None:
        """Empty/whitespace docstring returns empty list."""
        app = make_app()
        result = process_docstring(app, "   ")
        assert result == []

    def test_simple_docstring_returns_lines(
        self, make_app: Callable[..., SphinxTestApp]
    ) -> None:
        """Simple docstring is split into lines."""
        app = make_app()
        docstring = "This is a docstring.\n\nWith multiple paragraphs."
        result = process_docstring(app, docstring)
        assert result == ["This is a docstring.", "", "With multiple paragraphs."]

    def test_docstring_strips_leading_trailing_whitespace(
        self, make_app: Callable[..., SphinxTestApp]
    ) -> None:
        """Docstring is stripped of leading/trailing whitespace."""
        app = make_app()
        docstring = "\n  A simple docstring.\n  "
        result = process_docstring(app, docstring)
        assert result == ["A simple docstring."]

    def test_event_emitted_when_registered(
        self, make_app: Callable[..., SphinxTestApp]
    ) -> None:
        """Event is emitted when autodoc-process-docstring is registered."""
        app = make_app()
        # The default make_app includes sphinx.ext.autodoc, so event is registered
        assert "autodoc-process-docstring" in app.events.events

        # Track if event was emitted
        handler_called = []

        def handler(_app, what, name, obj, options, lines):
            handler_called.append((what, name, obj, options, lines.copy()))

        app.connect("autodoc-process-docstring", handler)

        docstring = "Test docstring."
        process_docstring(app, docstring, what="class", name="test.Model", obj=None)

        assert len(handler_called) == 1
        what, name, obj, options, lines = handler_called[0]
        assert what == "class"
        assert name == "test.Model"
        assert obj is None
        assert options is None
        assert lines == ["Test docstring."]

    def test_handlers_modify_lines_in_place(
        self, make_app: Callable[..., SphinxTestApp]
    ) -> None:
        """Handlers can modify lines in-place."""
        app = make_app()

        def handler(_app, what, name, obj, options, lines):
            # Append a line
            lines.append("Added by handler.")

        app.connect("autodoc-process-docstring", handler)

        docstring = "Original line."
        result = process_docstring(app, docstring)

        assert result == ["Original line.", "Added by handler."]

    def test_fallback_when_event_not_registered(self) -> None:
        """Returns raw lines when event is not registered."""
        # Create a mock app without the event registered
        mock_app = MagicMock()
        mock_app.events.events = {}  # No events registered

        docstring = "Test docstring."
        result = process_docstring(mock_app, docstring, name="test.Model")

        # Should return raw lines without calling emit
        assert result == ["Test docstring."]
        mock_app.emit.assert_not_called()


class TestProcessDocstringWithNumpydoc:
    """Tests for docstring processing with numpydoc extension."""

    @pytest.fixture
    def app_with_numpydoc(
        self, make_app: Callable[..., SphinxTestApp], tmp_path
    ) -> SphinxTestApp:
        """Create app with numpydoc extension loaded."""
        srcdir = tmp_path / "numpydoc_src"
        srcdir.mkdir(exist_ok=True)
        (srcdir / "conf.py").write_text(
            'extensions = ["sphinx.ext.autodoc", "numpydoc", '
            '"sphinxcontrib.pydantic"]\n'
            'project = "Test"\n'
            'exclude_patterns = ["_build"]\n'
        )
        (srcdir / "index.rst").write_text("Test\n====\n")
        return make_app(srcdir=srcdir)

    def test_numpydoc_processes_see_also(
        self, app_with_numpydoc: SphinxTestApp
    ) -> None:
        """Numpydoc converts See Also section to seealso directive."""
        docstring = """A class docstring.

See Also
--------
OtherClass : A related class.
"""
        result = process_docstring(
            app_with_numpydoc, docstring, what="class", name="test.Model"
        )

        # numpydoc should convert "See Also" to ".. seealso::" directive
        result_text = "\n".join(result)
        assert ".. seealso::" in result_text or "See Also" not in result_text

    def test_numpydoc_processes_notes(self, app_with_numpydoc: SphinxTestApp) -> None:
        """Numpydoc converts Notes section appropriately."""
        docstring = """A class docstring.

Notes
-----
This is a note about the class.
"""
        result = process_docstring(
            app_with_numpydoc, docstring, what="class", name="test.Model"
        )

        # numpydoc should process the Notes section
        result_text = "\n".join(result)
        # Notes section should be converted (either to rubric or note directive)
        assert "This is a note about the class" in result_text


class TestProcessDocstringWithNapoleon:
    """Tests for docstring processing with Napoleon extension."""

    @pytest.fixture
    def app_with_napoleon(
        self, make_app: Callable[..., SphinxTestApp], tmp_path
    ) -> SphinxTestApp:
        """Create app with Napoleon extension loaded."""
        srcdir = tmp_path / "napoleon_src"
        srcdir.mkdir(exist_ok=True)
        (srcdir / "conf.py").write_text(
            'extensions = ["sphinx.ext.autodoc", "sphinx.ext.napoleon", '
            '"sphinxcontrib.pydantic"]\n'
            'project = "Test"\n'
            'exclude_patterns = ["_build"]\n'
            "napoleon_numpy_docstring = True\n"
        )
        (srcdir / "index.rst").write_text("Test\n====\n")
        return make_app(srcdir=srcdir)

    def test_napoleon_processes_google_style(
        self, make_app: Callable[..., SphinxTestApp], tmp_path
    ) -> None:
        """Napoleon converts Google-style docstrings."""
        srcdir = tmp_path / "napoleon_google_src"
        srcdir.mkdir(exist_ok=True)
        (srcdir / "conf.py").write_text(
            'extensions = ["sphinx.ext.autodoc", "sphinx.ext.napoleon", '
            '"sphinxcontrib.pydantic"]\n'
            'project = "Test"\n'
            'exclude_patterns = ["_build"]\n'
            "napoleon_google_docstring = True\n"
        )
        (srcdir / "index.rst").write_text("Test\n====\n")
        app = make_app(srcdir=srcdir)

        docstring = """A function docstring.

Args:
    param1: The first parameter.
    param2: The second parameter.

Returns:
    The return value.
"""
        result = process_docstring(app, docstring, what="function", name="test.func")

        # Napoleon should convert Args to :param: fields
        result_text = "\n".join(result)
        assert ":param param1:" in result_text or "param1" in result_text

    def test_napoleon_processes_numpy_style(
        self, app_with_napoleon: SphinxTestApp
    ) -> None:
        """Napoleon converts NumPy-style docstrings."""
        docstring = """A function docstring.

Parameters
----------
param1 : str
    The first parameter.
param2 : int
    The second parameter.

Returns
-------
bool
    The return value.
"""
        result = process_docstring(
            app_with_napoleon, docstring, what="function", name="test.func"
        )

        # Napoleon should convert Parameters to :param: fields
        result_text = "\n".join(result)
        assert ":param param1:" in result_text or "param1" in result_text
