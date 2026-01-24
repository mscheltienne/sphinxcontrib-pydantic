"""Integration tests for cross-reference functionality."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from bs4 import BeautifulSoup
from sphinx.testing.util import SphinxTestApp


class TestCrossReferenceResolution:
    """Tests for cross-reference resolution during build."""

    def test_validator_summary_has_xrefs(
        self,
        make_app: Callable[..., SphinxTestApp],
        tmp_path: Path,
        parse_html: Callable[[str], BeautifulSoup],
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
        soup = parse_html((outdir / "index.html").read_text())

        # Find the Validators summary table
        validators_table = None
        for table in soup.select("table.docutils"):
            caption = table.select_one("caption")
            if caption and "Validators" in caption.get_text():
                validators_table = table
                break

        assert validators_table is not None, "Validators summary table not found"

        # Verify validator cross-reference exists in the table
        validator_links = validators_table.select("a.reference.internal")
        validator_hrefs = [link.get("href", "") for link in validator_links]

        # Should have a link to check_positive
        assert any(
            "check_positive" in href for href in validator_hrefs
        ), f"Expected link to check_positive, found: {validator_hrefs}"

        # Verify the link text is correct
        validator_texts = [link.get_text(strip=True) for link in validator_links]
        assert "check_positive" in validator_texts

    def test_build_succeeds_with_validators(
        self,
        make_app: Callable[..., SphinxTestApp],
        tmp_path: Path,
        parse_html: Callable[[str], BeautifulSoup],
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
        soup = parse_html((outdir / "index.html").read_text())

        # Verify class is documented
        class_sigs = soup.select("dl.py.class dt.sig")
        class_names = {
            sig.select_one("span.sig-name.descname").get_text(strip=True)
            for sig in class_sigs
            if sig.select_one("span.sig-name.descname")
        }
        assert "MultiFieldValidator" in class_names

        # Verify validator method is documented
        method_sigs = soup.select("dl.py.method dt.sig")
        method_ids = {sig.get("id", "") for sig in method_sigs}
        assert any("check_bounds" in mid for mid in method_ids)

    def test_html_contains_validator_names(
        self,
        make_app: Callable[..., SphinxTestApp],
        tmp_path: Path,
        parse_html: Callable[[str], BeautifulSoup],
    ) -> None:
        """Test that HTML output contains validator names in proper structure."""
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
        soup = parse_html((outdir / "index.html").read_text())

        # Validator should be documented as a method
        validator_sig = soup.select_one(
            "dl.py.method dt.sig#tests\\.assets\\.models\\.validators\\."
            "SingleFieldValidator\\.check_positive"
        )
        assert validator_sig is not None, "Validator check_positive not documented"

        # Verify the method name
        method_name = validator_sig.select_one("span.sig-name.descname")
        assert method_name is not None
        assert method_name.get_text(strip=True) == "check_positive"

    def test_model_validator_documented(
        self,
        make_app: Callable[..., SphinxTestApp],
        tmp_path: Path,
        parse_html: Callable[[str], BeautifulSoup],
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
        soup = parse_html((outdir / "index.html").read_text())

        # Model validator should be documented as a method
        validator_sig = soup.select_one(
            "dl.py.method dt.sig#tests\\.assets\\.models\\.validators\\."
            "ModelValidatorAfter\\.passwords_match"
        )
        assert validator_sig is not None, "Model validator passwords_match not documented"

        # Verify the method name
        method_name = validator_sig.select_one("span.sig-name.descname")
        assert method_name is not None
        assert method_name.get_text(strip=True) == "passwords_match"


class TestValidatorTableStructure:
    """Tests for validator table HTML structure."""

    def test_validator_table_has_correct_columns(
        self,
        make_app: Callable[..., SphinxTestApp],
        tmp_path: Path,
        parse_html: Callable[[str], BeautifulSoup],
    ) -> None:
        """Test that validator summary table has correct column structure."""
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
            ".. autoclass:: tests.assets.models.validators.MultiFieldValidator\n"
            "   :members:\n"
        )

        app = make_app(srcdir=srcdir)
        app.build()

        assert app.statuscode == 0

        outdir = Path(app.outdir)
        soup = parse_html((outdir / "index.html").read_text())

        # Find the Validators table
        validators_table = None
        for table in soup.select("table.docutils"):
            caption = table.select_one("caption")
            if caption and "Validators" in caption.get_text():
                validators_table = table
                break

        assert validators_table is not None, "Validators table not found"

        # Verify table headers
        headers = [th.get_text(strip=True) for th in validators_table.select("thead th")]
        assert "Validator" in headers, f"Expected 'Validator' header, got: {headers}"
        assert "Mode" in headers, f"Expected 'Mode' header, got: {headers}"
        assert "Fields" in headers, f"Expected 'Fields' header, got: {headers}"

        # Verify table has data rows
        data_rows = validators_table.select("tbody tr")
        assert len(data_rows) >= 1, "Expected at least one validator row"

        # Verify first row has validator link
        first_row = data_rows[0]
        validator_cell = first_row.select_one("td:first-child")
        assert validator_cell is not None
        validator_link = validator_cell.select_one("a.reference.internal")
        assert validator_link is not None, "Validator should be a cross-reference link"
