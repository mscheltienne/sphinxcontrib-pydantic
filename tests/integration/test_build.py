"""Integration tests for full Sphinx builds."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from sphinx.testing.util import SphinxTestApp


class TestSphinxBuild:
    """Tests for complete Sphinx builds with our extension."""

    def test_build_completes_without_errors(
        self,
        make_app: Callable[..., SphinxTestApp],
        tmp_path: Path,
    ) -> None:
        """Test that a basic build completes without errors."""
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
            "This is a test.\n"
        )

        app = make_app(srcdir=srcdir)
        app.build()

        # Check no errors occurred
        assert app.statuscode == 0

    def test_build_with_pydantic_model_directive(
        self,
        make_app: Callable[..., SphinxTestApp],
        tmp_path: Path,
    ) -> None:
        """Test that pydantic-model directive works in build."""
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
            ".. pydantic-model:: tests.assets.models.basic.SimpleModel\n"
        )

        app = make_app(srcdir=srcdir)
        app.build()

        assert app.statuscode == 0

    def test_build_with_pydantic_settings_directive(
        self,
        make_app: Callable[..., SphinxTestApp],
        tmp_path: Path,
    ) -> None:
        """Test that pydantic-settings directive works in build."""
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
            ".. pydantic-settings:: tests.assets.models.settings.SimpleSettings\n"
        )

        app = make_app(srcdir=srcdir)
        app.build()

        assert app.statuscode == 0

    def test_build_with_json_schema_option(
        self,
        make_app: Callable[..., SphinxTestApp],
        tmp_path: Path,
    ) -> None:
        """Test that show-json option works in build."""
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
            ".. pydantic-model:: tests.assets.models.basic.SimpleModel\n"
            "   :show-json:\n"
        )

        app = make_app(srcdir=srcdir)
        app.build()

        assert app.statuscode == 0

    def test_build_generates_html_output(
        self,
        make_app: Callable[..., SphinxTestApp],
        tmp_path: Path,
    ) -> None:
        """Test that build generates HTML output files."""
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
            ".. pydantic-model:: tests.assets.models.basic.SimpleModel\n"
        )

        app = make_app(srcdir=srcdir)
        app.build()

        # Check that HTML was generated
        outdir = Path(app.outdir)
        assert (outdir / "index.html").exists()

    def test_html_contains_model_name(
        self,
        make_app: Callable[..., SphinxTestApp],
        tmp_path: Path,
    ) -> None:
        """Test that generated HTML contains the model name."""
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
            ".. pydantic-model:: tests.assets.models.basic.SimpleModel\n"
        )

        app = make_app(srcdir=srcdir)
        app.build()

        outdir = Path(app.outdir)
        html_content = (outdir / "index.html").read_text()

        assert "SimpleModel" in html_content

    def test_html_contains_field_names(
        self,
        make_app: Callable[..., SphinxTestApp],
        tmp_path: Path,
    ) -> None:
        """Test that generated HTML contains field names from field summary."""
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
            ".. pydantic-model:: tests.assets.models.basic.SimpleModel\n"
            "   :show-field-summary:\n"
        )

        app = make_app(srcdir=srcdir)
        app.build()

        outdir = Path(app.outdir)
        html_content = (outdir / "index.html").read_text()

        # SimpleModel has 'name' and 'count' fields
        assert "name" in html_content
        assert "count" in html_content


class TestBuildWarnings:
    """Tests for build warnings."""

    def test_no_warnings_for_valid_model(
        self,
        make_app: Callable[..., SphinxTestApp],
        tmp_path: Path,
    ) -> None:
        """Test that no warnings are generated for valid models."""
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
            ".. pydantic-model:: tests.assets.models.basic.SimpleModel\n"
        )

        app = make_app(srcdir=srcdir)
        app.build()

        # Get warnings from the warning stream
        warnings = app._warning.getvalue()

        # Should have no warnings about our model
        assert "SimpleModel" not in warnings or "Cannot find" not in warnings

    def test_warning_for_nonexistent_model(
        self,
        make_app: Callable[..., SphinxTestApp],
        tmp_path: Path,
    ) -> None:
        """Test that a warning is generated for nonexistent models."""
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
            ".. pydantic-model:: nonexistent.module.FakeModel\n"
        )

        app = make_app(srcdir=srcdir)
        app.build()

        warnings = app._warning.getvalue()

        # Should have a warning about the model
        assert "Cannot find" in warnings or "FakeModel" in warnings


class TestMultipleModels:
    """Tests for documenting multiple models."""

    def test_build_with_multiple_models(
        self,
        make_app: Callable[..., SphinxTestApp],
        tmp_path: Path,
    ) -> None:
        """Test that multiple models can be documented."""
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
            ".. pydantic-model:: tests.assets.models.basic.SimpleModel\n"
            "\n"
            ".. pydantic-model:: tests.assets.models.basic.DocumentedModel\n"
            "\n"
            ".. pydantic-model:: tests.assets.models.fields.FieldWithConstraints\n"
        )

        app = make_app(srcdir=srcdir)
        app.build()

        assert app.statuscode == 0

        outdir = Path(app.outdir)
        html_content = (outdir / "index.html").read_text()

        assert "SimpleModel" in html_content
        assert "DocumentedModel" in html_content
        assert "FieldWithConstraints" in html_content
