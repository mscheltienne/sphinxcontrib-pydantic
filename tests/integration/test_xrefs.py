"""Integration tests for cross-reference functionality."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from sphinx.testing.util import SphinxTestApp


class TestCrossReferenceResolution:
    """Tests for cross-reference resolution during build."""

    def test_validator_summary_has_xrefs(
        self,
        make_app: Callable[..., SphinxTestApp],
        tmp_path: Path,
    ) -> None:
        """Test that validator summary contains cross-references."""
        srcdir = tmp_path / "src"
        srcdir.mkdir()

        (srcdir / "conf.py").write_text(
            'extensions = ["sphinx.ext.autodoc", "sphinxcontrib.pydantic"]\n'
            'project = "Test"\n'
            'exclude_patterns = ["_build"]\n'
            "sphinxcontrib_pydantic_model_show_validator_summary = True\n"
        )
        (srcdir / "index.rst").write_text(
            "Test Project\n"
            "============\n"
            "\n"
            ".. autoclass:: tests.assets.models.validators.SingleFieldValidator\n"
            "   :members:\n"
        )

        app = make_app(srcdir=srcdir)
        app.build()

        assert app.statuscode == 0

        outdir = Path(app.outdir)
        html = (outdir / "index.html").read_text()

        assert "SingleFieldValidator" in html
        assert "check_positive" in html
        assert "value" in html

    def test_build_succeeds_with_validators(
        self,
        make_app: Callable[..., SphinxTestApp],
        tmp_path: Path,
    ) -> None:
        """Test that build succeeds when documenting validators."""
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
            ".. autoclass:: tests.assets.models.validators.MultiFieldValidator\n"
            "   :members:\n"
        )

        app = make_app(srcdir=srcdir)
        app.build()

        assert app.statuscode == 0

        outdir = Path(app.outdir)
        html = (outdir / "index.html").read_text()

        assert "MultiFieldValidator" in html
        assert "check_bounds" in html

    def test_html_contains_validator_names(
        self,
        make_app: Callable[..., SphinxTestApp],
        tmp_path: Path,
    ) -> None:
        """Test that HTML output contains validator names."""
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
            ".. autoclass:: tests.assets.models.validators.SingleFieldValidator\n"
            "   :members:\n"
        )

        app = make_app(srcdir=srcdir)
        app.build()

        outdir = Path(app.outdir)
        html_content = (outdir / "index.html").read_text()

        assert "check_positive" in html_content

    def test_model_validator_documented(
        self,
        make_app: Callable[..., SphinxTestApp],
        tmp_path: Path,
    ) -> None:
        """Test that model validators are documented."""
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
            ".. autoclass:: tests.assets.models.validators.ModelValidatorAfter\n"
            "   :members:\n"
        )

        app = make_app(srcdir=srcdir)
        app.build()

        assert app.statuscode == 0

        outdir = Path(app.outdir)
        html_content = (outdir / "index.html").read_text()

        assert "passwords_match" in html_content
