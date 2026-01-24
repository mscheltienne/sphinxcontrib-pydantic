"""Integration tests for RootModel documentation."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from sphinx.testing.util import SphinxTestApp


class TestRootModelDocumentation:
    """Test that RootModel classes are documented correctly."""

    def test_root_model_generates_root_type_line(
        self,
        make_app: Callable[..., SphinxTestApp],
        tmp_path: Path,
    ) -> None:
        """Test that RootModel shows 'Root Type' instead of field table."""
        srcdir = tmp_path / "src"
        srcdir.mkdir()

        (srcdir / "conf.py").write_text(
            'extensions = ["sphinx.ext.autodoc", "sphinxcontrib.pydantic"]\n'
            'project = "Test"\n'
            'exclude_patterns = ["_build"]\n'
        )
        (srcdir / "index.rst").write_text(
            "Test Project\n"
            "============\n"
            "\n"
            ".. autoclass:: tests.assets.models.root_model.IntList\n"
            "   :members:\n"
        )

        app = make_app(srcdir=srcdir)
        app.build()

        assert app.statuscode == 0

        outdir = Path(app.outdir)
        index_html = (outdir / "index.html").read_text()

        # Should contain IntList class
        assert "IntList" in index_html
        # Should contain 'Root Type' instead of a field table with 'root'
        assert "Root Type" in index_html
        assert "list[int]" in index_html or "list" in index_html

    def test_root_model_with_validator_shows_validators(
        self,
        make_app: Callable[..., SphinxTestApp],
        tmp_path: Path,
    ) -> None:
        """Test that RootModel with validators shows validator summary."""
        srcdir = tmp_path / "src"
        srcdir.mkdir()

        (srcdir / "conf.py").write_text(
            'extensions = ["sphinx.ext.autodoc", "sphinxcontrib.pydantic"]\n'
            'project = "Test"\n'
            'exclude_patterns = ["_build"]\n'
        )
        (srcdir / "index.rst").write_text(
            "Test Project\n"
            "============\n"
            "\n"
            ".. autoclass:: tests.assets.models.root_model.ConstrainedIntList\n"
            "   :members:\n"
        )

        app = make_app(srcdir=srcdir)
        app.build()

        assert app.statuscode == 0

        outdir = Path(app.outdir)
        index_html = (outdir / "index.html").read_text()

        # Should show the validator
        assert "check_positive" in index_html

    def test_string_mapping_root_model(
        self,
        make_app: Callable[..., SphinxTestApp],
        tmp_path: Path,
    ) -> None:
        """Test that dict-based RootModel is documented."""
        srcdir = tmp_path / "src"
        srcdir.mkdir()

        (srcdir / "conf.py").write_text(
            'extensions = ["sphinx.ext.autodoc", "sphinxcontrib.pydantic"]\n'
            'project = "Test"\n'
            'exclude_patterns = ["_build"]\n'
        )
        (srcdir / "index.rst").write_text(
            "Test Project\n"
            "============\n"
            "\n"
            ".. autoclass:: tests.assets.models.root_model.StringMapping\n"
            "   :members:\n"
        )

        app = make_app(srcdir=srcdir)
        app.build()

        assert app.statuscode == 0

        outdir = Path(app.outdir)
        index_html = (outdir / "index.html").read_text()

        # Should contain the dict type
        assert "Root Type" in index_html
        assert "dict" in index_html

    def test_nested_root_model(
        self,
        make_app: Callable[..., SphinxTestApp],
        tmp_path: Path,
    ) -> None:
        """Test that nested RootModel is documented."""
        srcdir = tmp_path / "src"
        srcdir.mkdir()

        (srcdir / "conf.py").write_text(
            'extensions = ["sphinx.ext.autodoc", "sphinxcontrib.pydantic"]\n'
            'project = "Test"\n'
            'exclude_patterns = ["_build"]\n'
        )
        (srcdir / "index.rst").write_text(
            "Test Project\n"
            "============\n"
            "\n"
            ".. autoclass:: tests.assets.models.root_model.NestedModel\n"
            "   :members:\n"
        )

        app = make_app(srcdir=srcdir)
        app.build()

        assert app.statuscode == 0

        outdir = Path(app.outdir)
        index_html = (outdir / "index.html").read_text()

        # Should contain the nested type
        assert "Root Type" in index_html


class TestRootModelAutomodule:
    """Test RootModel documentation via automodule."""

    def test_automodule_documents_root_models(
        self,
        make_app: Callable[..., SphinxTestApp],
        tmp_path: Path,
    ) -> None:
        """Test that automodule documents RootModel classes."""
        srcdir = tmp_path / "src"
        srcdir.mkdir()

        (srcdir / "conf.py").write_text(
            'extensions = ["sphinx.ext.autodoc", "sphinxcontrib.pydantic"]\n'
            'project = "Test"\n'
            'exclude_patterns = ["_build"]\n'
        )
        (srcdir / "index.rst").write_text(
            "Test Project\n"
            "============\n"
            "\n"
            ".. automodule:: tests.assets.models.root_model\n"
            "   :members:\n"
        )

        app = make_app(srcdir=srcdir)
        app.build()

        assert app.statuscode == 0

        outdir = Path(app.outdir)
        index_html = (outdir / "index.html").read_text()

        # All RootModel classes should be documented
        assert "IntList" in index_html
        assert "StringMapping" in index_html
        assert "ConstrainedIntList" in index_html
        assert "NestedModel" in index_html
