"""Integration tests for inheritance scenarios."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from bs4 import BeautifulSoup
from sphinx.testing.util import SphinxTestApp


class TestInheritanceDocumentation:
    """Tests for documenting inherited models."""

    def test_child_model_documented(
        self,
        make_app: Callable[..., SphinxTestApp],
        tmp_path: Path,
        parse_html: Callable[[str], BeautifulSoup],
    ) -> None:
        """Test basic child model documentation."""
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
            ".. autoclass:: tests.assets.models.inheritance.ChildModelSimple\n"
            "   :members:\n"
        )

        app = make_app(srcdir=srcdir)
        app.build()

        assert app.statuscode == 0

        outdir = Path(app.outdir)
        soup = parse_html((outdir / "index.html").read_text(encoding="utf-8"))

        # Verify class is documented
        class_sig = soup.select_one(
            "dt.sig#tests\\.assets\\.models\\.inheritance\\.ChildModelSimple"
        )
        assert class_sig is not None, "ChildModelSimple class not found"

        # Verify child_field appears in the documentation
        content = soup.select_one("dl.py.class dd")
        assert content is not None
        assert "child_field" in content.get_text()

    def test_inherited_members_shows_parent_fields(
        self,
        make_app: Callable[..., SphinxTestApp],
        tmp_path: Path,
        parse_html: Callable[[str], BeautifulSoup],
    ) -> None:
        """Test that inherited-members shows parent fields."""
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
            ".. autoclass:: tests.assets.models.inheritance.ChildModelSimple\n"
            "   :members:\n"
            "   :inherited-members: BaseModel\n"
        )

        app = make_app(srcdir=srcdir)
        app.build()

        assert app.statuscode == 0

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

        # Verify both child and parent fields appear
        field_cells = fields_table.select("tbody tr td:first-child")
        field_names = {cell.get_text(strip=True) for cell in field_cells}
        assert "child_field" in field_names, "Expected child_field in table"
        assert "base_field" in field_names, "Expected inherited base_field in table"

    def test_child_with_own_validator(
        self,
        make_app: Callable[..., SphinxTestApp],
        tmp_path: Path,
        parse_html: Callable[[str], BeautifulSoup],
    ) -> None:
        """Test child model with its own validator."""
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
            ".. autoclass:: tests.assets.models.inheritance.ChildModelWithOwnValidator\n"  # noqa: E501
            "   :members:\n"
        )

        app = make_app(srcdir=srcdir)
        app.build()

        assert app.statuscode == 0

        outdir = Path(app.outdir)
        soup = parse_html((outdir / "index.html").read_text(encoding="utf-8"))

        # Verify the validator method is documented
        validator_sig = soup.select_one(
            "dl.py.method dt.sig#tests\\.assets\\.models\\.inheritance\\."
            "ChildModelWithOwnValidator\\.validate_child_field"
        )
        assert validator_sig is not None, (
            "Validator validate_child_field not documented"
        )


class TestMultiLevelInheritance:
    """Tests for multi-level inheritance."""

    def test_three_level_inheritance(
        self,
        make_app: Callable[..., SphinxTestApp],
        tmp_path: Path,
        parse_html: Callable[[str], BeautifulSoup],
    ) -> None:
        """Test documentation of three-level inheritance."""
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
            ".. autoclass:: tests.assets.models.inheritance.GrandchildModel\n"
            "   :members:\n"
            "   :inherited-members: BaseModel\n"
        )

        app = make_app(srcdir=srcdir)
        app.build()

        assert app.statuscode == 0

        outdir = Path(app.outdir)
        soup = parse_html((outdir / "index.html").read_text(encoding="utf-8"))

        # Verify class is documented
        class_sig = soup.select_one(
            "dt.sig#tests\\.assets\\.models\\.inheritance\\.GrandchildModel"
        )
        assert class_sig is not None, "GrandchildModel class not found"

        # Verify grandchild_field appears in documentation
        content = soup.select_one("dl.py.class dd")
        assert content is not None
        assert "grandchild_field" in content.get_text()


class TestInheritedModelValidators:
    """Tests for inherited model validators."""

    def test_child_with_inherited_model_validator(
        self,
        make_app: Callable[..., SphinxTestApp],
        tmp_path: Path,
        parse_html: Callable[[str], BeautifulSoup],
    ) -> None:
        """Test child model that inherits a model validator."""
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
            ".. autoclass:: tests.assets.models.inheritance.ChildWithInheritedModelValidator\n"  # noqa: E501
            "   :members:\n"
        )

        app = make_app(srcdir=srcdir)
        app.build()

        assert app.statuscode == 0

        outdir = Path(app.outdir)
        soup = parse_html((outdir / "index.html").read_text(encoding="utf-8"))

        # Verify class is documented
        class_sig = soup.select_one(
            "dt.sig#tests\\.assets\\.models\\.inheritance\\."
            "ChildWithInheritedModelValidator"
        )
        assert class_sig is not None, "ChildWithInheritedModelValidator not found"

        # Verify class name in signature
        class_name = class_sig.select_one("span.sig-name.descname")
        assert class_name is not None
        assert class_name.get_text(strip=True) == "ChildWithInheritedModelValidator"
