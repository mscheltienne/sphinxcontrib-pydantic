"""Integration tests for autodoc integration."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from bs4 import BeautifulSoup
from sphinx.testing.util import SphinxTestApp


class TestAutodocIntegration:
    """Tests for autodoc integration with Pydantic models."""

    def test_automodule_documents_pydantic_models(
        self,
        make_app: Callable[..., SphinxTestApp],
        tmp_path: Path,
        parse_html: Callable[[str], BeautifulSoup],
    ) -> None:
        """Test that automodule correctly documents Pydantic models."""
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
            ".. automodule:: tests.assets.models.basic\n"
            "   :members:\n"
        )

        app = make_app(srcdir=srcdir)
        app.build()

        assert app.statuscode == 0

        outdir = Path(app.outdir)
        soup = parse_html((outdir / "index.html").read_text(encoding="utf-8"))

        # Verify models are documented as proper class definitions
        class_sigs = soup.select("dl.py.class dt.sig")
        documented_classes = {sig.get("id", "").split(".")[-1] for sig in class_sigs}
        assert "SimpleModel" in documented_classes
        assert "EmptyModel" in documented_classes

    def test_autoclass_documents_pydantic_model(
        self,
        make_app: Callable[..., SphinxTestApp],
        tmp_path: Path,
        parse_html: Callable[[str], BeautifulSoup],
    ) -> None:
        """Test that autoclass correctly documents a Pydantic model."""
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
            ".. autoclass:: tests.assets.models.basic.SimpleModel\n"
            "   :members:\n"
        )

        app = make_app(srcdir=srcdir)
        app.build()

        assert app.statuscode == 0

        outdir = Path(app.outdir)
        soup = parse_html((outdir / "index.html").read_text(encoding="utf-8"))

        # Verify the class is documented with correct structure
        class_sig = soup.select_one(
            "dt.sig#tests\\.assets\\.models\\.basic\\.SimpleModel"
        )
        assert class_sig is not None

        # Verify class name appears in signature
        class_name = class_sig.select_one("span.sig-name.descname")
        assert class_name is not None
        assert class_name.get_text(strip=True) == "SimpleModel"

    def test_autodoc_skips_pydantic_internals(
        self,
        make_app: Callable[..., SphinxTestApp],
        tmp_path: Path,
        parse_html: Callable[[str], BeautifulSoup],
    ) -> None:
        """Test that autodoc skips Pydantic internal attributes."""
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
            ".. autoclass:: tests.assets.models.basic.SimpleModel\n"
            "   :members:\n"
            "   :undoc-members:\n"
        )

        app = make_app(srcdir=srcdir)
        app.build()

        outdir = Path(app.outdir)
        soup = parse_html((outdir / "index.html").read_text(encoding="utf-8"))

        # Get all documented member IDs (methods and attributes)
        all_sigs = soup.select("dl.py.method dt.sig, dl.py.attribute dt.sig")
        documented_member_ids = {sig.get("id", "") for sig in all_sigs}

        # These pydantic internals must NOT be documented
        pydantic_internals = {
            "__pydantic_complete__",
            "__pydantic_decorators__",
            "__pydantic_fields_set__",
            "__pydantic_private__",
            "__pydantic_validator__",
            "__pydantic_core_schema__",
            "__pydantic_serializer__",
        }

        # Check that none of the internals appear in documented members
        for internal in pydantic_internals:
            for member_id in documented_member_ids:
                assert internal not in member_id, (
                    f"Pydantic internal '{internal}' should not be documented"
                )

    def test_autodoc_shows_field_summary(
        self,
        make_app: Callable[..., SphinxTestApp],
        tmp_path: Path,
        parse_html: Callable[[str], BeautifulSoup],
    ) -> None:
        """Test that autodoc shows field summary for Pydantic models."""
        srcdir = tmp_path / "src"
        srcdir.mkdir()

        (srcdir / "conf.py").write_text(
            'extensions = ["sphinx.ext.autodoc", "sphinxcontrib.pydantic"]\n'
            'project = "Test"\n'
            'exclude_patterns = ["_build"]\n'
            "sphinxcontrib_pydantic_model_show_field_summary = True\n"
        )
        (srcdir / "index.rst").write_text(
            "Test Project\n"
            "============\n"
            "\n"
            ".. autoclass:: tests.assets.models.basic.SimpleModel\n"
            "   :members:\n"
        )

        app = make_app(srcdir=srcdir)
        app.build()

        outdir = Path(app.outdir)
        soup = parse_html((outdir / "index.html").read_text(encoding="utf-8"))

        # Find the Fields table by its caption
        fields_table = None
        for table in soup.select("table.docutils"):
            caption = table.select_one("caption")
            if caption and "Fields" in caption.get_text():
                fields_table = table
                break

        assert fields_table is not None, "Fields summary table not found"

        # Verify table has correct header structure
        headers = [th.get_text(strip=True) for th in fields_table.select("thead th")]
        assert "Field" in headers
        assert "Type" in headers

        # Verify field names appear in table body
        field_cells = fields_table.select("tbody tr td:first-child")
        field_names = {cell.get_text(strip=True) for cell in field_cells}
        assert "name" in field_names
        assert "count" in field_names


class TestAutodocWithValidators:
    """Tests for autodoc integration with validators."""

    def test_autodoc_documents_model_with_validators(
        self,
        make_app: Callable[..., SphinxTestApp],
        tmp_path: Path,
        parse_html: Callable[[str], BeautifulSoup],
    ) -> None:
        """Test that autodoc documents models with validators."""
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

        assert app.statuscode == 0

        outdir = Path(app.outdir)
        soup = parse_html((outdir / "index.html").read_text(encoding="utf-8"))

        # Verify class is documented
        class_sig = soup.select_one(
            "dt.sig#tests\\.assets\\.models\\.validators\\.SingleFieldValidator"
        )
        assert class_sig is not None

        # Verify validator method is documented
        validator_sig = soup.select_one(
            "dt.sig#tests\\.assets\\.models\\.validators\\."
            "SingleFieldValidator\\.check_positive"
        )
        assert validator_sig is not None


class TestAutodocWithSettings:
    """Tests for autodoc integration with BaseSettings."""

    def test_autodoc_documents_settings(
        self,
        make_app: Callable[..., SphinxTestApp],
        tmp_path: Path,
        parse_html: Callable[[str], BeautifulSoup],
    ) -> None:
        """Test that autodoc documents BaseSettings models."""
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
            ".. autoclass:: tests.assets.models.settings.SimpleSettings\n"
            "   :members:\n"
        )

        app = make_app(srcdir=srcdir)
        app.build()

        assert app.statuscode == 0

        outdir = Path(app.outdir)
        soup = parse_html((outdir / "index.html").read_text(encoding="utf-8"))

        # Verify settings class is documented with proper structure
        class_sig = soup.select_one(
            "dt.sig#tests\\.assets\\.models\\.settings\\.SimpleSettings"
        )
        assert class_sig is not None

        class_name = class_sig.select_one("span.sig-name.descname")
        assert class_name is not None
        assert class_name.get_text(strip=True) == "SimpleSettings"


class TestConfigurationEffects:
    """Tests for configuration option effects on autodoc."""

    def test_disable_field_summary(
        self,
        make_app: Callable[..., SphinxTestApp],
        tmp_path: Path,
        parse_html: Callable[[str], BeautifulSoup],
    ) -> None:
        """Test that field summary can be disabled via config."""
        srcdir = tmp_path / "src"
        srcdir.mkdir()

        (srcdir / "conf.py").write_text(
            'extensions = ["sphinx.ext.autodoc", "sphinxcontrib.pydantic"]\n'
            'project = "Test"\n'
            'exclude_patterns = ["_build"]\n'
            "sphinxcontrib_pydantic_model_show_field_summary = False\n"
        )
        (srcdir / "index.rst").write_text(
            "Test Project\n"
            "============\n"
            "\n"
            ".. autoclass:: tests.assets.models.basic.SimpleModel\n"
            "   :members:\n"
        )

        app = make_app(srcdir=srcdir)
        app.build()

        assert app.statuscode == 0

        outdir = Path(app.outdir)
        soup = parse_html((outdir / "index.html").read_text(encoding="utf-8"))

        # Model should be documented
        class_sig = soup.select_one(
            "dt.sig#tests\\.assets\\.models\\.basic\\.SimpleModel"
        )
        assert class_sig is not None

        # Field summary table should NOT be present
        fields_table = None
        for table in soup.select("table.docutils"):
            caption = table.select_one("caption")
            if caption and "Fields" in caption.get_text():
                fields_table = table
                break

        assert fields_table is None, "Fields table should not be present when disabled"

    def test_custom_signature_prefix(
        self,
        make_app: Callable[..., SphinxTestApp],
        tmp_path: Path,
        parse_html: Callable[[str], BeautifulSoup],
    ) -> None:
        """Test that custom signature prefix works."""
        srcdir = tmp_path / "src"
        srcdir.mkdir()

        (srcdir / "conf.py").write_text(
            'extensions = ["sphinx.ext.autodoc", "sphinxcontrib.pydantic"]\n'
            'project = "Test"\n'
            'exclude_patterns = ["_build"]\n'
            'sphinxcontrib_pydantic_model_signature_prefix = "pydantic model"\n'
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

        # Find the signature containing SimpleModel
        class_sig = None
        for sig in soup.select("dt.sig"):
            name_span = sig.select_one("span.sig-name.descname")
            if name_span and name_span.get_text(strip=True) == "SimpleModel":
                class_sig = sig
                break

        assert class_sig is not None, "SimpleModel signature not found"

        # Verify the signature prefix span contains our custom prefix
        prefix_span = class_sig.select_one("span.property")
        assert prefix_span is not None, "Signature prefix span not found"
        prefix_text = prefix_span.get_text(strip=True)
        assert "pydantic" in prefix_text, (
            f"Expected 'pydantic' in prefix, got: {prefix_text}"
        )
        assert "model" in prefix_text, f"Expected 'model' in prefix, got: {prefix_text}"
