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
        soup = parse_html((outdir / "index.html").read_text(encoding="utf-8"))

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
        assert any("check_positive" in href for href in validator_hrefs), (
            f"Expected link to check_positive, found: {validator_hrefs}"
        )

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
        soup = parse_html((outdir / "index.html").read_text(encoding="utf-8"))

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
        soup = parse_html((outdir / "index.html").read_text(encoding="utf-8"))

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
        soup = parse_html((outdir / "index.html").read_text(encoding="utf-8"))

        # Model validator should be documented as a method
        validator_sig = soup.select_one(
            "dl.py.method dt.sig#tests\\.assets\\.models\\.validators\\."
            "ModelValidatorAfter\\.passwords_match"
        )
        assert validator_sig is not None, (
            "Model validator passwords_match not documented"
        )

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
        soup = parse_html((outdir / "index.html").read_text(encoding="utf-8"))

        # Find the Validators table
        validators_table = None
        for table in soup.select("table.docutils"):
            caption = table.select_one("caption")
            if caption and "Validators" in caption.get_text():
                validators_table = table
                break

        assert validators_table is not None, "Validators table not found"

        # Verify table headers
        headers = [
            th.get_text(strip=True) for th in validators_table.select("thead th")
        ]
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


class TestFieldCrossReferences:
    """Tests for field cross-reference resolution."""

    def test_field_summary_table_has_field_xrefs(
        self,
        make_app: Callable[..., SphinxTestApp],
        tmp_path: Path,
        parse_html: Callable[[str], BeautifulSoup],
    ) -> None:
        """Test that field summary table has cross-references for field names."""
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

        assert app.statuscode == 0

        outdir = Path(app.outdir)
        soup = parse_html((outdir / "index.html").read_text(encoding="utf-8"))

        # Find the Fields summary table
        fields_table = None
        for table in soup.select("table.docutils"):
            caption = table.select_one("caption")
            if caption and "Fields" in caption.get_text():
                fields_table = table
                break

        assert fields_table is not None, "Fields summary table not found"

        # Verify field names are cross-references (links)
        field_links = fields_table.select("a.reference.internal")
        field_hrefs = [link.get("href", "") for link in field_links]

        # Should have links to name and count fields
        assert any("name" in href for href in field_hrefs), (
            f"Expected link to 'name' field, found: {field_hrefs}"
        )
        assert any("count" in href for href in field_hrefs), (
            f"Expected link to 'count' field, found: {field_hrefs}"
        )

    def test_field_documentation_section_exists(
        self,
        make_app: Callable[..., SphinxTestApp],
        tmp_path: Path,
        parse_html: Callable[[str], BeautifulSoup],
    ) -> None:
        """Test that detailed field documentation section appears."""
        srcdir = tmp_path / "src"
        srcdir.mkdir()

        (srcdir / "conf.py").write_text(
            'extensions = ["sphinx.ext.autodoc", "sphinxcontrib.pydantic"]\n'
            'project = "Test"\n'
            'exclude_patterns = ["_build"]\n'
            "sphinxcontrib_pydantic_model_show_field_doc = True\n"
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

        # Find field documentation - pydantic_field directive renders as
        # dl.py.pydantic_field
        field_docs = soup.select("dl.py.pydantic_field")

        # Should have at least 2 field docs (name and count)
        assert len(field_docs) >= 2, (
            f"Expected at least 2 field documentation sections, found {len(field_docs)}"
        )

    def test_field_doc_includes_description(
        self,
        make_app: Callable[..., SphinxTestApp],
        tmp_path: Path,
        parse_html: Callable[[str], BeautifulSoup],
    ) -> None:
        """Test that field documentation includes description from Field()."""
        srcdir = tmp_path / "src"
        srcdir.mkdir()

        (srcdir / "conf.py").write_text(
            'extensions = ["sphinx.ext.autodoc", "sphinxcontrib.pydantic"]\n'
            'project = "Test"\n'
            'exclude_patterns = ["_build"]\n'
            "sphinxcontrib_pydantic_model_show_field_doc = True\n"
        )
        (srcdir / "index.rst").write_text(
            "Test Project\n"
            "============\n"
            "\n"
            ".. autoclass:: tests.assets.models.fields.FieldWithMetadata\n"
            "   :members:\n"
        )

        app = make_app(srcdir=srcdir)
        app.build()

        assert app.statuscode == 0

        outdir = Path(app.outdir)
        soup = parse_html((outdir / "index.html").read_text(encoding="utf-8"))

        # The description should appear in the HTML
        html_text = soup.get_text()
        assert "A documented field." in html_text, (
            "Field description not found in HTML output"
        )

    def test_field_doc_can_be_disabled(
        self,
        make_app: Callable[..., SphinxTestApp],
        tmp_path: Path,
        parse_html: Callable[[str], BeautifulSoup],
    ) -> None:
        """Test that field documentation can be disabled via config."""
        srcdir = tmp_path / "src"
        srcdir.mkdir()

        (srcdir / "conf.py").write_text(
            'extensions = ["sphinx.ext.autodoc", "sphinxcontrib.pydantic"]\n'
            'project = "Test"\n'
            'exclude_patterns = ["_build"]\n'
            "sphinxcontrib_pydantic_model_show_field_doc = False\n"
        )
        (srcdir / "index.rst").write_text(
            "Test Project\n"
            "============\n"
            "\n"
            ".. autoclass:: tests.assets.models.fields.FieldWithMetadata\n"
            "   :members:\n"
        )

        app = make_app(srcdir=srcdir)
        app.build()

        assert app.statuscode == 0

        outdir = Path(app.outdir)
        soup = parse_html((outdir / "index.html").read_text(encoding="utf-8"))

        # When disabled, the detailed description should NOT appear
        # We check that the description text is not present in the HTML
        html_text = soup.get_text()
        assert "A documented field." not in html_text, (
            "Field description should not appear when show_field_doc=False"
        )

    def test_type_annotations_are_cross_references(
        self,
        make_app: Callable[..., SphinxTestApp],
        tmp_path: Path,
        parse_html: Callable[[str], BeautifulSoup],
    ) -> None:
        """Test that type annotations in field table are cross-references."""
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

        assert app.statuscode == 0

        outdir = Path(app.outdir)
        soup = parse_html((outdir / "index.html").read_text(encoding="utf-8"))

        # Find the Fields summary table
        fields_table = None
        for table in soup.select("table.docutils"):
            caption = table.select_one("caption")
            if caption and "Fields" in caption.get_text():
                fields_table = table
                break

        assert fields_table is not None, "Fields summary table not found"

        # Type column should contain cross-reference elements
        # RST cross-refs render as code.xref.py.py-class elements
        type_xrefs = fields_table.select("code.xref.py.py-class")
        type_texts = [xref.get_text(strip=True) for xref in type_xrefs]

        # str and int types should be xref elements
        assert "str" in type_texts, (
            f"Expected 'str' type to be a cross-reference, found: {type_texts}"
        )
        assert "int" in type_texts, (
            f"Expected 'int' type to be a cross-reference, found: {type_texts}"
        )
