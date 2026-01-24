"""Integration tests for full Sphinx builds."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from bs4 import BeautifulSoup
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
            "Test Project\n============\n\nThis is a test.\n"
        )

        app = make_app(srcdir=srcdir)
        app.build()

        # Check no errors occurred
        assert app.statuscode == 0

    def test_build_with_pydantic_model_directive(
        self,
        make_app: Callable[..., SphinxTestApp],
        tmp_path: Path,
        parse_html: Callable[[str], BeautifulSoup],
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

        outdir = Path(app.outdir)
        soup = parse_html((outdir / "index.html").read_text(encoding="utf-8"))

        # Verify model is documented as a class
        class_sig = None
        for sig in soup.select("dt.sig"):
            name_span = sig.select_one("span.sig-name.descname")
            if name_span and name_span.get_text(strip=True) == "SimpleModel":
                class_sig = sig
                break

        assert class_sig is not None, "SimpleModel not found in output"

    def test_build_with_pydantic_settings_directive(
        self,
        make_app: Callable[..., SphinxTestApp],
        tmp_path: Path,
        parse_html: Callable[[str], BeautifulSoup],
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

        outdir = Path(app.outdir)
        soup = parse_html((outdir / "index.html").read_text(encoding="utf-8"))

        # Verify settings class is documented
        class_sig = None
        for sig in soup.select("dt.sig"):
            name_span = sig.select_one("span.sig-name.descname")
            if name_span and name_span.get_text(strip=True) == "SimpleSettings":
                class_sig = sig
                break

        assert class_sig is not None, "SimpleSettings not found in output"

    def test_build_with_json_schema_option(
        self,
        make_app: Callable[..., SphinxTestApp],
        tmp_path: Path,
        parse_html: Callable[[str], BeautifulSoup],
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

        outdir = Path(app.outdir)
        soup = parse_html((outdir / "index.html").read_text(encoding="utf-8"))

        # Verify JSON code block exists with correct highlighting class
        json_block = soup.select_one("div.highlight-json")
        assert json_block is not None, "JSON code block not found"

        # Verify JSON content has expected structure (type and properties)
        json_content = json_block.get_text()
        assert "type" in json_content, "JSON schema should contain 'type'"
        assert "properties" in json_content or "string" in json_content

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
        parse_html: Callable[[str], BeautifulSoup],
    ) -> None:
        """Test that generated HTML contains the model name in proper structure."""
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
        soup = parse_html((outdir / "index.html").read_text(encoding="utf-8"))

        # Verify model name appears in the signature structure
        class_names = {
            sig.select_one("span.sig-name.descname").get_text(strip=True)
            for sig in soup.select("dt.sig")
            if sig.select_one("span.sig-name.descname")
        }
        assert "SimpleModel" in class_names

    def test_html_contains_field_names(
        self,
        make_app: Callable[..., SphinxTestApp],
        tmp_path: Path,
        parse_html: Callable[[str], BeautifulSoup],
    ) -> None:
        """Test that generated HTML contains field names in field summary table."""
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
        soup = parse_html((outdir / "index.html").read_text(encoding="utf-8"))

        # Find the Fields table
        fields_table = None
        for table in soup.select("table.docutils"):
            caption = table.select_one("caption")
            if caption and "Fields" in caption.get_text():
                fields_table = table
                break

        assert fields_table is not None, "Fields table not found"

        # Verify field names appear in table body
        field_cells = fields_table.select("tbody tr td:first-child")
        field_names = {cell.get_text(strip=True) for cell in field_cells}
        assert "name" in field_names, f"Expected 'name' field, got: {field_names}"
        assert "count" in field_names, f"Expected 'count' field, got: {field_names}"


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
        assert "Cannot find" not in warnings
        assert "SimpleModel" not in warnings or "error" not in warnings.lower()

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

        # Warning should mention the missing model
        assert "FakeModel" in warnings or "nonexistent" in warnings

    def test_no_nitpick_warnings_for_constrained_fields(
        self,
        make_app: Callable[..., SphinxTestApp],
        tmp_path: Path,
    ) -> None:
        """Test that no nitpick warnings are generated for constrained fields.

        With hide_paramlist=True (default), the signature is hidden, so there are
        no cross-reference warnings for annotated_types.Ge, annotated_types.MinLen,
        etc.

        This test uses autoclass (not pydantic-model) because autoclass generates
        the full signature with Annotated types, which is where the warnings come from.
        """
        srcdir = tmp_path / "src"
        srcdir.mkdir()

        (srcdir / "conf.py").write_text(
            'extensions = ["sphinx.ext.autodoc", "sphinxcontrib.pydantic"]\n'
            'project = "Test"\n'
            'exclude_patterns = ["_build"]\n'
            "nitpicky = True\n"
        )
        (srcdir / "index.rst").write_text(
            "Test Project\n"
            "============\n"
            "\n"
            ".. autoclass:: tests.assets.models.fields.FieldWithConstraints\n"
            "   :members:\n"
        )

        app = make_app(srcdir=srcdir)
        app.build()

        warnings = app._warning.getvalue()

        # Should have no warnings about annotated_types or pydantic internals
        assert "annotated_types" not in warnings, (
            f"Unexpected annotated_types warnings:\n{warnings}"
        )
        assert "_PydanticGeneralMetadata" not in warnings, (
            f"Unexpected _PydanticGeneralMetadata warnings:\n{warnings}"
        )

    def test_model_hide_paramlist_true_hides_signature(
        self,
        make_app: Callable[..., SphinxTestApp],
        tmp_path: Path,
        parse_html: Callable[[str], BeautifulSoup],
    ) -> None:
        """Test that model signature is hidden when hide_paramlist=True (default)."""
        srcdir = tmp_path / "src"
        srcdir.mkdir()

        (srcdir / "conf.py").write_text(
            'extensions = ["sphinx.ext.autodoc", "sphinxcontrib.pydantic"]\n'
            'project = "Test"\n'
            'exclude_patterns = ["_build"]\n'
            # Default: sphinxcontrib_pydantic_model_hide_paramlist = True
        )
        (srcdir / "index.rst").write_text(
            "Test Project\n"
            "============\n"
            "\n"
            ".. autoclass:: tests.assets.models.basic.SimpleModel\n"
        )

        app = make_app(srcdir=srcdir)
        app.build()

        outdir = Path(app.outdir)
        soup = parse_html((outdir / "index.html").read_text(encoding="utf-8"))

        # Find SimpleModel's signature
        for sig in soup.select("dt.sig"):
            name_span = sig.select_one("span.sig-name.descname")
            if name_span and name_span.get_text(strip=True) == "SimpleModel":
                # Should have no parameter list (just empty parens or nothing)
                sig_text = sig.get_text()
                # The signature should NOT contain parameter names like "name" or "count"
                assert "name:" not in sig_text or "sig-param" not in str(sig), (
                    f"Signature should be hidden but found: {sig_text}"
                )
                break
        else:
            raise AssertionError("SimpleModel not found in output")

    def test_model_hide_paramlist_false_shows_signature(
        self,
        make_app: Callable[..., SphinxTestApp],
        tmp_path: Path,
        parse_html: Callable[[str], BeautifulSoup],
    ) -> None:
        """Test that model signature is shown when hide_paramlist=False."""
        srcdir = tmp_path / "src"
        srcdir.mkdir()

        (srcdir / "conf.py").write_text(
            'extensions = ["sphinx.ext.autodoc", "sphinxcontrib.pydantic"]\n'
            'project = "Test"\n'
            'exclude_patterns = ["_build"]\n'
            "sphinxcontrib_pydantic_model_hide_paramlist = False\n"
        )
        (srcdir / "index.rst").write_text(
            "Test Project\n"
            "============\n"
            "\n"
            ".. autoclass:: tests.assets.models.basic.SimpleModel\n"
        )

        app = make_app(srcdir=srcdir)
        app.build()

        outdir = Path(app.outdir)
        soup = parse_html((outdir / "index.html").read_text(encoding="utf-8"))

        # Find SimpleModel's signature
        for sig in soup.select("dt.sig"):
            name_span = sig.select_one("span.sig-name.descname")
            if name_span and name_span.get_text(strip=True) == "SimpleModel":
                # Should have parameter list with field names
                sig_params = sig.select("em.sig-param")
                assert len(sig_params) > 0, (
                    f"Expected parameters in signature but found: {sig.get_text()}"
                )
                break
        else:
            raise AssertionError("SimpleModel not found in output")

    def test_settings_hide_paramlist_true_no_warnings(
        self,
        make_app: Callable[..., SphinxTestApp],
        tmp_path: Path,
    ) -> None:
        """Test that settings signature is hidden by default, avoiding warnings.

        BaseSettings has many internal parameters with types that can't be
        resolved (DotenvType, CliSettingsSource, etc.). With hide_paramlist=True,
        these don't generate warnings.
        """
        srcdir = tmp_path / "src"
        srcdir.mkdir()

        (srcdir / "conf.py").write_text(
            'extensions = ["sphinx.ext.autodoc", "sphinxcontrib.pydantic"]\n'
            'project = "Test"\n'
            'exclude_patterns = ["_build"]\n'
            "nitpicky = True\n"
            # Default: sphinxcontrib_pydantic_settings_hide_paramlist = True
        )
        (srcdir / "index.rst").write_text(
            "Test Project\n"
            "============\n"
            "\n"
            ".. autoclass:: tests.assets.models.settings.SimpleSettings\n"
        )

        app = make_app(srcdir=srcdir)
        app.build()

        warnings = app._warning.getvalue()

        # Should have no warnings about pydantic_settings internal types
        assert "DotenvType" not in warnings, (
            f"Unexpected DotenvType warnings:\n{warnings}"
        )
        assert "CliSettingsSource" not in warnings, (
            f"Unexpected CliSettingsSource warnings:\n{warnings}"
        )
        assert "_case_sensitive" not in warnings, (
            f"Unexpected BaseSettings parameter warnings:\n{warnings}"
        )


class TestMultipleModels:
    """Tests for documenting multiple models."""

    def test_build_with_multiple_models(
        self,
        make_app: Callable[..., SphinxTestApp],
        tmp_path: Path,
        parse_html: Callable[[str], BeautifulSoup],
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
        soup = parse_html((outdir / "index.html").read_text(encoding="utf-8"))

        # Verify all models are documented
        class_names = {
            sig.select_one("span.sig-name.descname").get_text(strip=True)
            for sig in soup.select("dt.sig")
            if sig.select_one("span.sig-name.descname")
        }
        assert "SimpleModel" in class_names
        assert "DocumentedModel" in class_names
        assert "FieldWithConstraints" in class_names
