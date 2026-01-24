"""SQLModel test models."""

from __future__ import annotations

from sqlmodel import Field, Relationship, SQLModel


class Team(SQLModel, table=True):
    """A team in the database."""

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    headquarters: str

    heroes: list[Hero] = Relationship(back_populates="team")


class Hero(SQLModel, table=True):
    """A hero in the database."""

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    secret_name: str
    age: int | None = Field(default=None, index=True)

    team_id: int | None = Field(default=None, foreign_key="team.id")
    team: Team | None = Relationship(back_populates="heroes")


class HeroRead(SQLModel):
    """Read model for Hero (DTO)."""

    id: int
    name: str
    secret_name: str
    age: int | None = None


class HeroReadWithTeam(HeroRead):
    """Read model for Hero with team info."""

    team: Team | None = None


class HeroCreate(SQLModel):
    """Create model for Hero."""

    name: str
    secret_name: str
    age: int | None = None
    team_id: int | None = None


class HeroUpdate(SQLModel):
    """Update model for Hero."""

    name: str | None = None
    secret_name: str | None = None
    age: int | None = None
    team_id: int | None = None
