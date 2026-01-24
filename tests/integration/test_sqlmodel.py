"""Integration tests for SQLModel models."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from bs4 import BeautifulSoup
from sphinx.testing.util import SphinxTestApp


class TestSQLModelTableDocumentation:
    """Tests for documenting SQLModel table models."""

    def test_team_table_documented(
        self,
        make_app: Callable[..., SphinxTestApp],
        tmp_path: Path,
        parse_html: Callable[[str], BeautifulSoup],
    ) -> None:
        """Test that Team table model is documented correctly."""
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
            ".. autoclass:: tests.assets.models.sqlmodel_models.Team\n"
            "   :members:\n"
        )

        app = make_app(srcdir=srcdir)
        app.build()

        assert app.statuscode == 0

        outdir = Path(app.outdir)
        soup = parse_html((outdir / "index.html").read_text())

        # Verify class is documented
        class_sig = soup.select_one(
            "dt.sig#tests\\.assets\\.models\\.sqlmodel_models\\.Team"
        )
        assert class_sig is not None, "Team class not found"

        # Verify fields are documented
        content = soup.select_one("dl.py.class dd")
        assert content is not None
        content_text = content.get_text()
        assert "name" in content_text
        assert "headquarters" in content_text

    def test_hero_table_documented(
        self,
        make_app: Callable[..., SphinxTestApp],
        tmp_path: Path,
        parse_html: Callable[[str], BeautifulSoup],
    ) -> None:
        """Test that Hero table model with relationships is documented."""
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
            ".. autoclass:: tests.assets.models.sqlmodel_models.Hero\n"
            "   :members:\n"
        )

        app = make_app(srcdir=srcdir)
        app.build()

        assert app.statuscode == 0

        outdir = Path(app.outdir)
        soup = parse_html((outdir / "index.html").read_text())

        # Verify class is documented
        class_sig = soup.select_one(
            "dt.sig#tests\\.assets\\.models\\.sqlmodel_models\\.Hero"
        )
        assert class_sig is not None, "Hero class not found"

        # Verify fields are documented
        content = soup.select_one("dl.py.class dd")
        assert content is not None
        content_text = content.get_text()
        assert "name" in content_text
        assert "secret_name" in content_text


class TestSQLModelDTODocumentation:
    """Tests for documenting SQLModel DTO models (non-table)."""

    def test_hero_read_dto(
        self,
        make_app: Callable[..., SphinxTestApp],
        tmp_path: Path,
        parse_html: Callable[[str], BeautifulSoup],
    ) -> None:
        """Test that HeroRead DTO is documented correctly."""
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
            ".. autoclass:: tests.assets.models.sqlmodel_models.HeroRead\n"
            "   :members:\n"
        )

        app = make_app(srcdir=srcdir)
        app.build()

        assert app.statuscode == 0

        outdir = Path(app.outdir)
        soup = parse_html((outdir / "index.html").read_text())

        # Verify class is documented
        class_sig = soup.select_one(
            "dt.sig#tests\\.assets\\.models\\.sqlmodel_models\\.HeroRead"
        )
        assert class_sig is not None, "HeroRead class not found"

        # Verify id field is documented
        content = soup.select_one("dl.py.class dd")
        assert content is not None
        assert "id" in content.get_text()

    def test_hero_create_dto(
        self,
        make_app: Callable[..., SphinxTestApp],
        tmp_path: Path,
        parse_html: Callable[[str], BeautifulSoup],
    ) -> None:
        """Test that HeroCreate DTO is documented correctly."""
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
            ".. autoclass:: tests.assets.models.sqlmodel_models.HeroCreate\n"
            "   :members:\n"
        )

        app = make_app(srcdir=srcdir)
        app.build()

        assert app.statuscode == 0

        outdir = Path(app.outdir)
        soup = parse_html((outdir / "index.html").read_text())

        # Verify class is documented
        class_sig = soup.select_one(
            "dt.sig#tests\\.assets\\.models\\.sqlmodel_models\\.HeroCreate"
        )
        assert class_sig is not None, "HeroCreate class not found"

        # Verify fields are documented
        content = soup.select_one("dl.py.class dd")
        assert content is not None
        content_text = content.get_text()
        assert "name" in content_text
        assert "secret_name" in content_text

    def test_hero_update_dto(
        self,
        make_app: Callable[..., SphinxTestApp],
        tmp_path: Path,
        parse_html: Callable[[str], BeautifulSoup],
    ) -> None:
        """Test that HeroUpdate DTO is documented correctly."""
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
            ".. autoclass:: tests.assets.models.sqlmodel_models.HeroUpdate\n"
            "   :members:\n"
        )

        app = make_app(srcdir=srcdir)
        app.build()

        assert app.statuscode == 0

        outdir = Path(app.outdir)
        soup = parse_html((outdir / "index.html").read_text())

        # Verify class is documented
        class_sig = soup.select_one(
            "dt.sig#tests\\.assets\\.models\\.sqlmodel_models\\.HeroUpdate"
        )
        assert class_sig is not None, "HeroUpdate class not found"

        # Verify name field is documented
        content = soup.select_one("dl.py.class dd")
        assert content is not None
        assert "name" in content.get_text()


class TestSQLModelInheritance:
    """Tests for SQLModel inheritance patterns."""

    def test_hero_read_with_team_inheritance(
        self,
        make_app: Callable[..., SphinxTestApp],
        tmp_path: Path,
        parse_html: Callable[[str], BeautifulSoup],
    ) -> None:
        """Test that HeroReadWithTeam (inherits from HeroRead) is documented."""
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
            ".. autoclass:: tests.assets.models.sqlmodel_models.HeroReadWithTeam\n"
            "   :members:\n"
            "   :inherited-members: BaseModel\n"
        )

        app = make_app(srcdir=srcdir)
        app.build()

        assert app.statuscode == 0

        outdir = Path(app.outdir)
        soup = parse_html((outdir / "index.html").read_text())

        # Verify class is documented
        class_sig = soup.select_one(
            "dt.sig#tests\\.assets\\.models\\.sqlmodel_models\\.HeroReadWithTeam"
        )
        assert class_sig is not None, "HeroReadWithTeam class not found"

        # Verify team field is documented
        content = soup.select_one("dl.py.class dd")
        assert content is not None
        assert "team" in content.get_text()


class TestSQLModelModule:
    """Tests for documenting entire SQLModel module."""

    def test_automodule_sqlmodel_models(
        self,
        make_app: Callable[..., SphinxTestApp],
        tmp_path: Path,
        parse_html: Callable[[str], BeautifulSoup],
    ) -> None:
        """Test documenting entire SQLModel module."""
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
            ".. automodule:: tests.assets.models.sqlmodel_models\n"
            "   :members:\n"
        )

        app = make_app(srcdir=srcdir)
        app.build()

        assert app.statuscode == 0

        outdir = Path(app.outdir)
        soup = parse_html((outdir / "index.html").read_text())

        # Verify all models are documented
        class_sigs = soup.select("dl.py.class dt.sig")
        documented_classes = {sig.get("id", "").split(".")[-1] for sig in class_sigs}

        assert "Team" in documented_classes
        assert "Hero" in documented_classes
        assert "HeroRead" in documented_classes
        assert "HeroCreate" in documented_classes
