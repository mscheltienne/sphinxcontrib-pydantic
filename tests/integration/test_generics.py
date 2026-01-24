"""Integration tests for generic models."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from sphinx.testing.util import SphinxTestApp


class TestGenericModelDocumentation:
    """Tests for documenting generic models."""

    def test_generic_model_documented(
        self,
        make_app: Callable[..., SphinxTestApp],
        tmp_path: Path,
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
        html = (outdir / "index.html").read_text()

        assert "GenericContainer" in html
        assert "value" in html
        assert "label" in html

    def test_concrete_generic_documented(
        self,
        make_app: Callable[..., SphinxTestApp],
        tmp_path: Path,
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
        html = (outdir / "index.html").read_text()

        assert "ConcreteContainer" in html
        assert "multiplier" in html

    def test_generic_with_validator(
        self,
        make_app: Callable[..., SphinxTestApp],
        tmp_path: Path,
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
        html = (outdir / "index.html").read_text()

        assert "GenericWithValidator" in html
        assert "validate_name" in html

    def test_concrete_generic_with_inherited_validator(
        self,
        make_app: Callable[..., SphinxTestApp],
        tmp_path: Path,
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
        html = (outdir / "index.html").read_text()
        assert "ConcreteWithValidator" in html

    def test_bounded_generic(
        self,
        make_app: Callable[..., SphinxTestApp],
        tmp_path: Path,
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
        html = (outdir / "index.html").read_text()

        assert "BoundedGeneric" in html
        assert "validate_items_not_empty" in html


class TestMultipleTypeParameters:
    """Tests for generics with multiple type parameters."""

    def test_generic_mapping(
        self,
        make_app: Callable[..., SphinxTestApp],
        tmp_path: Path,
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
        html = (outdir / "index.html").read_text()

        assert "GenericMapping" in html
        assert "key" in html
        assert "value" in html
