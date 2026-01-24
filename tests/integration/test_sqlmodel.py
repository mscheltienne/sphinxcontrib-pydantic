"""Integration tests for SQLModel models."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from sphinx.testing.util import SphinxTestApp


class TestSQLModelTableDocumentation:
    """Tests for documenting SQLModel table models."""

    def test_team_table_documented(
        self,
        make_app: Callable[..., SphinxTestApp],
        tmp_path: Path,
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
        html = (outdir / "index.html").read_text()

        assert "Team" in html
        assert "name" in html
        assert "headquarters" in html

    def test_hero_table_documented(
        self,
        make_app: Callable[..., SphinxTestApp],
        tmp_path: Path,
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
        html = (outdir / "index.html").read_text()

        assert "Hero" in html
        assert "name" in html
        assert "secret_name" in html


class TestSQLModelDTODocumentation:
    """Tests for documenting SQLModel DTO models (non-table)."""

    def test_hero_read_dto(
        self,
        make_app: Callable[..., SphinxTestApp],
        tmp_path: Path,
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
        html = (outdir / "index.html").read_text()

        assert "HeroRead" in html
        assert "id" in html

    def test_hero_create_dto(
        self,
        make_app: Callable[..., SphinxTestApp],
        tmp_path: Path,
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
        html = (outdir / "index.html").read_text()

        assert "HeroCreate" in html
        assert "name" in html
        assert "secret_name" in html

    def test_hero_update_dto(
        self,
        make_app: Callable[..., SphinxTestApp],
        tmp_path: Path,
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
        html = (outdir / "index.html").read_text()

        assert "HeroUpdate" in html
        assert "name" in html


class TestSQLModelInheritance:
    """Tests for SQLModel inheritance patterns."""

    def test_hero_read_with_team_inheritance(
        self,
        make_app: Callable[..., SphinxTestApp],
        tmp_path: Path,
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
        html = (outdir / "index.html").read_text()

        assert "HeroReadWithTeam" in html
        assert "team" in html


class TestSQLModelModule:
    """Tests for documenting entire SQLModel module."""

    def test_automodule_sqlmodel_models(
        self,
        make_app: Callable[..., SphinxTestApp],
        tmp_path: Path,
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
        html = (outdir / "index.html").read_text()

        # All models should be documented
        assert "Team" in html
        assert "Hero" in html
        assert "HeroRead" in html
        assert "HeroCreate" in html
