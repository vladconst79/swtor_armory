from datetime import date

from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import ActiveMixin, IdMixin, OwnedModelMixin, TimestampMixin


class Character(IdMixin, TimestampMixin, ActiveMixin, OwnedModelMixin, Base):
    __tablename__ = "characters"

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    display_name: Mapped[str | None] = mapped_column(String(255))
    sequence: Mapped[int] = mapped_column(Integer, nullable=False, server_default="10")
    faction: Mapped[str] = mapped_column(String(50), nullable=False)
    origin_story_id: Mapped[int | None] = mapped_column(ForeignKey("origin_stories.id"), index=True)
    level: Mapped[int | None] = mapped_column(Integer)
    race: Mapped[str | None] = mapped_column(String(50))
    gender: Mapped[str | None] = mapped_column(String(50))
    server: Mapped[str | None] = mapped_column(String(50), index=True)
    guild: Mapped[str | None] = mapped_column(String(255))
    guild_id: Mapped[int | None] = mapped_column(ForeignKey("guilds.id"), index=True)
    alignment: Mapped[str | None] = mapped_column(String(50))
    notes: Mapped[str | None] = mapped_column(Text)
    valor_rank: Mapped[int | None] = mapped_column(Integer)
    crew_skills_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    mounts: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    titles: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")

    crew_skill_relations: Mapped[list["CharacterCrewSkillRelation"]] = relationship(
        back_populates="character",
        cascade="all, delete-orphan",
    )
    operation_lockouts: Mapped[list["OperationLockout"]] = relationship(
        back_populates="character",
        cascade="all, delete-orphan",
    )


class Loadout(IdMixin, TimestampMixin, ActiveMixin, OwnedModelMixin, Base):
    __tablename__ = "loadouts"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    sequence: Mapped[int] = mapped_column(Integer, nullable=False, server_default="10")
    loadout_type: Mapped[str] = mapped_column(String(50), nullable=False)
    loadout_url: Mapped[str | None] = mapped_column(String(2048))
    loadout_iframe: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)
    role_id: Mapped[int | None] = mapped_column(ForeignKey("roles.id"), index=True)
    spec_id: Mapped[int | None] = mapped_column(ForeignKey("specs.id"), index=True)


class Item(IdMixin, TimestampMixin, ActiveMixin, OwnedModelMixin, Base):
    __tablename__ = "items"

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    rarity: Mapped[str] = mapped_column(String(50), nullable=False, server_default="common", index=True)
    binding: Mapped[str] = mapped_column(String(50), nullable=False, server_default="none", index=True)
    bound: Mapped[bool] = mapped_column(nullable=False, server_default="false", index=True)
    cargo_hold: Mapped[str] = mapped_column(String(50), nullable=False, server_default="cargo_hold", index=True)
    cargo_bay: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1", index=True)


class CharacterCrewSkillRelation(IdMixin, TimestampMixin, ActiveMixin, OwnedModelMixin, Base):
    __tablename__ = "character_crew_skill_relations"

    name: Mapped[str | None] = mapped_column(String(255))
    display_name: Mapped[str | None] = mapped_column(String(255))
    character_id: Mapped[int] = mapped_column(ForeignKey("characters.id"), nullable=False, index=True)
    crew_skill_id: Mapped[int] = mapped_column(ForeignKey("crew_skills.id"), nullable=False, index=True)
    level: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
    skill_type: Mapped[str | None] = mapped_column(String(50))
    progress: Mapped[float] = mapped_column(Float, nullable=False, server_default="0")

    character: Mapped[Character] = relationship(back_populates="crew_skill_relations")


class OperationLockout(IdMixin, TimestampMixin, ActiveMixin, OwnedModelMixin, Base):
    __tablename__ = "operation_lockouts"

    name: Mapped[str | None] = mapped_column(String(255))
    week: Mapped[date | None] = mapped_column(index=True)
    character_id: Mapped[int] = mapped_column(ForeignKey("characters.id"), nullable=False, index=True)
    boss_id: Mapped[int] = mapped_column(ForeignKey("operation_bosses.id"), nullable=False, index=True)
    operation_id: Mapped[int] = mapped_column(ForeignKey("operations.id"), nullable=False, index=True)
    difficulty_id: Mapped[int] = mapped_column(ForeignKey("operation_difficulties.id"), nullable=False, index=True)
    completion_rate: Mapped[float] = mapped_column(Float, nullable=False, server_default="0")
    faction: Mapped[str | None] = mapped_column(String(50), index=True)

    character: Mapped[Character] = relationship(back_populates="operation_lockouts")
