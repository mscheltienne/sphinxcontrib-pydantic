"""Integration tests for RootModel documentation."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from bs4 import BeautifulSoup
from sphinx.testing.util import SphinxTestApp


class TestRootModelDocumentation:
    """Test that RootModel classes are documented correctly."""

    def test_root_model_generates_root_type_line(
        self,
        make_app: Callable[..., SphinxTestApp],
        tmp_path: Path,
        parse_html: Callable[[str], BeautifulSoup],
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
        soup = parse_html((outdir / "index.html").read_text())

        # Verify IntList class is documented
        class_sig = soup.select_one(
            "dt.sig#tests\\.assets\\.models\\.root_model\\.IntList"
        )
        assert class_sig is not None, "IntList class not found"

        # Find the class description (dd element after dt.sig)
        class_content = soup.select_one("dl.py.class dd")
        assert class_content is not None

        # Should contain 'Root Type' text
        content_text = class_content.get_text()
        assert "Root Type" in content_text, "Expected 'Root Type' in documentation"

        # Type should be fully rendered as list[int]
        assert "list[int]" in content_text, "Expected 'list[int]' type"

    def test_root_model_with_validator_shows_validators(
        self,
        make_app: Callable[..., SphinxTestApp],
        tmp_path: Path,
        parse_html: Callable[[str], BeautifulSoup],
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
        soup = parse_html((outdir / "index.html").read_text())

        # Verify class is documented
        class_sig = soup.select_one(
            "dt.sig#tests\\.assets\\.models\\.root_model\\.ConstrainedIntList"
        )
        assert class_sig is not None

        # Verify validator method is documented
        validator_sig = soup.select_one(
            "dl.py.method dt.sig#tests\\.assets\\.models\\.root_model\\."
            "ConstrainedIntList\\.check_positive"
        )
        assert validator_sig is not None, "Validator check_positive not documented"

    def test_string_mapping_root_model(
        self,
        make_app: Callable[..., SphinxTestApp],
        tmp_path: Path,
        parse_html: Callable[[str], BeautifulSoup],
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
        soup = parse_html((outdir / "index.html").read_text())

        # Verify class is documented
        class_sig = soup.select_one(
            "dt.sig#tests\\.assets\\.models\\.root_model\\.StringMapping"
        )
        assert class_sig is not None

        # Verify class content contains Root Type and dict
        class_content = soup.select_one("dl.py.class dd")
        assert class_content is not None
        content_text = class_content.get_text()
        assert "Root Type" in content_text
        assert "dict" in content_text

    def test_nested_root_model(
        self,
        make_app: Callable[..., SphinxTestApp],
        tmp_path: Path,
        parse_html: Callable[[str], BeautifulSoup],
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
        soup = parse_html((outdir / "index.html").read_text())

        # Verify class is documented
        class_sig = soup.select_one(
            "dt.sig#tests\\.assets\\.models\\.root_model\\.NestedModel"
        )
        assert class_sig is not None

        # Verify Root Type is in documentation
        class_content = soup.select_one("dl.py.class dd")
        assert class_content is not None
        assert "Root Type" in class_content.get_text()


class TestRootModelAutomodule:
    """Test RootModel documentation via automodule."""

    def test_automodule_documents_root_models(
        self,
        make_app: Callable[..., SphinxTestApp],
        tmp_path: Path,
        parse_html: Callable[[str], BeautifulSoup],
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
        soup = parse_html((outdir / "index.html").read_text())

        # Verify all RootModel classes are documented
        class_sigs = soup.select("dl.py.class dt.sig")
        documented_classes = {sig.get("id", "").split(".")[-1] for sig in class_sigs}

        assert "IntList" in documented_classes
        assert "StringMapping" in documented_classes
        assert "ConstrainedIntList" in documented_classes
        assert "NestedModel" in documented_classes
