"""Integration tests for generic models."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from bs4 import BeautifulSoup
from sphinx.testing.util import SphinxTestApp


class TestGenericModelDocumentation:
    """Tests for documenting generic models."""

    def test_generic_model_documented(
        self,
        make_app: Callable[..., SphinxTestApp],
        tmp_path: Path,
        parse_html: Callable[[str], BeautifulSoup],
    ) -> None:
        """Test generic model documentation."""
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
            ".. autoclass:: tests.assets.models.generics.GenericContainer\n"
            "   :members:\n"
        )

        app = make_app(srcdir=srcdir)
        app.build()

        assert app.statuscode == 0

        outdir = Path(app.outdir)
        soup = parse_html((outdir / "index.html").read_text(encoding="utf-8"))

        # Verify class is documented
        class_sig = soup.select_one(
            "dt.sig#tests\\.assets\\.models\\.generics\\.GenericContainer"
        )
        assert class_sig is not None, "GenericContainer class not found"

        # Verify fields are documented
        content = soup.select_one("dl.py.class dd")
        assert content is not None
        content_text = content.get_text()
        assert "value" in content_text
        assert "label" in content_text

    def test_concrete_generic_documented(
        self,
        make_app: Callable[..., SphinxTestApp],
        tmp_path: Path,
        parse_html: Callable[[str], BeautifulSoup],
    ) -> None:
        """Test concrete generic instantiation documentation."""
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
            ".. autoclass:: tests.assets.models.generics.ConcreteContainer\n"
            "   :members:\n"
        )

        app = make_app(srcdir=srcdir)
        app.build()

        assert app.statuscode == 0

        outdir = Path(app.outdir)
        soup = parse_html((outdir / "index.html").read_text(encoding="utf-8"))

        # Verify class is documented
        class_sig = soup.select_one(
            "dt.sig#tests\\.assets\\.models\\.generics\\.ConcreteContainer"
        )
        assert class_sig is not None, "ConcreteContainer class not found"

        # Verify multiplier field is documented
        content = soup.select_one("dl.py.class dd")
        assert content is not None
        assert "multiplier" in content.get_text()

    def test_generic_with_validator(
        self,
        make_app: Callable[..., SphinxTestApp],
        tmp_path: Path,
        parse_html: Callable[[str], BeautifulSoup],
    ) -> None:
        """Test generic model with validator."""
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
            ".. autoclass:: tests.assets.models.generics.GenericWithValidator\n"
            "   :members:\n"
        )

        app = make_app(srcdir=srcdir)
        app.build()

        assert app.statuscode == 0

        outdir = Path(app.outdir)
        soup = parse_html((outdir / "index.html").read_text(encoding="utf-8"))

        # Verify class is documented
        class_sig = soup.select_one(
            "dt.sig#tests\\.assets\\.models\\.generics\\.GenericWithValidator"
        )
        assert class_sig is not None, "GenericWithValidator class not found"

        # Verify validator method is documented
        validator_sig = soup.select_one(
            "dl.py.method dt.sig#tests\\.assets\\.models\\.generics\\."
            "GenericWithValidator\\.validate_name"
        )
        assert validator_sig is not None, "Validator validate_name not documented"

    def test_concrete_generic_with_inherited_validator(
        self,
        make_app: Callable[..., SphinxTestApp],
        tmp_path: Path,
        parse_html: Callable[[str], BeautifulSoup],
    ) -> None:
        """Test concrete generic with inherited validator."""
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
            ".. autoclass:: tests.assets.models.generics.ConcreteWithValidator\n"
            "   :members:\n"
        )

        app = make_app(srcdir=srcdir)
        app.build()

        assert app.statuscode == 0

        outdir = Path(app.outdir)
        soup = parse_html((outdir / "index.html").read_text(encoding="utf-8"))

        # Verify class is documented
        class_sig = soup.select_one(
            "dt.sig#tests\\.assets\\.models\\.generics\\.ConcreteWithValidator"
        )
        assert class_sig is not None, "ConcreteWithValidator class not found"

        # Verify class name in signature
        class_name = class_sig.select_one("span.sig-name.descname")
        assert class_name is not None
        assert class_name.get_text(strip=True) == "ConcreteWithValidator"

    def test_bounded_generic(
        self,
        make_app: Callable[..., SphinxTestApp],
        tmp_path: Path,
        parse_html: Callable[[str], BeautifulSoup],
    ) -> None:
        """Test generic with validated items."""
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
            ".. autoclass:: tests.assets.models.generics.BoundedGeneric\n"
            "   :members:\n"
        )

        app = make_app(srcdir=srcdir)
        app.build()

        assert app.statuscode == 0

        outdir = Path(app.outdir)
        soup = parse_html((outdir / "index.html").read_text(encoding="utf-8"))

        # Verify class is documented
        class_sig = soup.select_one(
            "dt.sig#tests\\.assets\\.models\\.generics\\.BoundedGeneric"
        )
        assert class_sig is not None, "BoundedGeneric class not found"

        # Verify validator method is documented
        validator_sig = soup.select_one(
            "dl.py.method dt.sig#tests\\.assets\\.models\\.generics\\."
            "BoundedGeneric\\.validate_items_not_empty"
        )
        assert validator_sig is not None, "Validator validate_items_not_empty not found"


class TestMultipleTypeParameters:
    """Tests for generics with multiple type parameters."""

    def test_generic_mapping(
        self,
        make_app: Callable[..., SphinxTestApp],
        tmp_path: Path,
        parse_html: Callable[[str], BeautifulSoup],
    ) -> None:
        """Test generic with multiple type parameters."""
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
            ".. autoclass:: tests.assets.models.generics.GenericMapping\n"
            "   :members:\n"
        )

        app = make_app(srcdir=srcdir)
        app.build()

        assert app.statuscode == 0

        outdir = Path(app.outdir)
        soup = parse_html((outdir / "index.html").read_text(encoding="utf-8"))

        # Verify class is documented
        class_sig = soup.select_one(
            "dt.sig#tests\\.assets\\.models\\.generics\\.GenericMapping"
        )
        assert class_sig is not None, "GenericMapping class not found"

        # Verify fields are documented in content
        content = soup.select_one("dl.py.class dd")
        assert content is not None
        content_text = content.get_text()
        assert "key" in content_text
        assert "value" in content_text
