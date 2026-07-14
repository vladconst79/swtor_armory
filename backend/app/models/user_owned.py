from datetime import date
from typing import ClassVar

from sqlalchemy import Float, ForeignKey, Integer, LargeBinary, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.db.base import Base
from app.models.associations import (
    character_class_names,
    character_items,
    character_loadouts,
    character_roles,
    character_titles,
    character_vehicles,
)
from app.models.mixins import ActiveMixin, IdMixin, OwnedModelMixin, TimestampMixin
from app.models.reference import ClassName, CrewSkill, Guild, OriginStory, Role, Title, Vehicle


class Character(IdMixin, TimestampMixin, ActiveMixin, OwnedModelMixin, Base):
    __tablename__ = "characters"

    MAX_LEVEL: ClassVar[int] = 80
    MAX_VALOR_RANK: ClassVar[int] = 100
    MAX_CLASS_NAMES: ClassVar[int] = 2
    MAX_CREW_SKILLS: ClassVar[int] = 3
    MAX_CRAFTING_CREW_SKILLS: ClassVar[int] = 1
    MAX_LOADOUTS: ClassVar[int] = 10

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
    faction_icon: Mapped[bytes | None] = mapped_column(LargeBinary)
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
    origin_story: Mapped[OriginStory | None] = relationship("OriginStory")
    guild_record: Mapped[Guild | None] = relationship("Guild")
    class_names: Mapped[list[ClassName]] = relationship(secondary=character_class_names, back_populates="characters")
    roles: Mapped[list[Role]] = relationship(secondary=character_roles, back_populates="characters")
    loadouts: Mapped[list["Loadout"]] = relationship(secondary=character_loadouts, back_populates="characters")
    items: Mapped[list["Item"]] = relationship(secondary=character_items, back_populates="characters")
    vehicle_records: Mapped[list[Vehicle]] = relationship(
        secondary=character_vehicles,
        back_populates="characters",
    )
    title_records: Mapped[list[Title]] = relationship(secondary=character_titles, back_populates="characters")

    @validates("level")
    def validate_level(self, key: str, level: int | None) -> int | None:
        if level is not None and not 1 <= level <= self.MAX_LEVEL:
            raise ValueError(f"Level must be between 1 and {self.MAX_LEVEL}.")
        return level

    @validates("valor_rank")
    def validate_valor_rank(self, key: str, valor_rank: int | None) -> int | None:
        if valor_rank is not None and not 1 <= valor_rank <= self.MAX_VALOR_RANK:
            raise ValueError(f"Valor rank must be between 1 and {self.MAX_VALOR_RANK}.")
        return valor_rank

    @property
    def available_roles(self) -> list[Role]:
        roles: list[Role] = []
        seen_keys: set[int] = set()
        for class_name in self.class_names:
            for role in class_name.roles:
                role_key = role.id if role.id is not None else id(role)
                if role_key not in seen_keys:
                    roles.append(role)
                    seen_keys.add(role_key)
        return roles

    def sync_derived_fields(self) -> None:
        self.display_name = self.derive_display_name()
        self.titles = len(self.title_records)
        self.mounts = len(self.vehicle_records)
        self.crew_skills_count = len(self.crew_skill_relations)

    def derive_display_name(self) -> str:
        guild_name = self.guild_record.name if self.guild_record is not None else self.guild
        if guild_name:
            return f"[{guild_name}] {self.name}"
        return self.name

    def validate_character_rules(self) -> None:
        self.validate_level("level", self.level)
        self.validate_valor_rank("valor_rank", self.valor_rank)
        self._validate_class_names()
        self._validate_crew_skills()
        self._validate_loadouts()

    def _validate_class_names(self) -> None:
        if len(self.class_names) > self.MAX_CLASS_NAMES:
            raise ValueError(f"A character can have no more than {self.MAX_CLASS_NAMES} class names.")

        if self.origin_story is None:
            return

        mismatched_class_names = [
            class_name.name
            for class_name in self.class_names
            if class_name.power_type != self.origin_story.power_type
        ]
        if mismatched_class_names:
            raise ValueError("Class names must have the same power type as the origin story.")

    def _validate_crew_skills(self) -> None:
        if len(self.crew_skill_relations) > self.MAX_CREW_SKILLS:
            raise ValueError(f"A character can have no more than {self.MAX_CREW_SKILLS} crew skills.")

        crafting_count = sum(
            1
            for relation in self.crew_skill_relations
            if relation.skill_type == "crafting"
            or (relation.crew_skill is not None and relation.crew_skill.skill_type == "crafting")
        )
        if crafting_count > self.MAX_CRAFTING_CREW_SKILLS:
            raise ValueError("A character can have no more than 1 crafting crew skill.")

    def _validate_loadouts(self) -> None:
        if len(self.loadouts) > self.MAX_LOADOUTS:
            raise ValueError(f"A character can have no more than {self.MAX_LOADOUTS} loadouts.")


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

    characters: Mapped[list[Character]] = relationship(secondary=character_loadouts, back_populates="loadouts")


class Item(IdMixin, TimestampMixin, ActiveMixin, OwnedModelMixin, Base):
    __tablename__ = "items"

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    rarity: Mapped[str] = mapped_column(String(50), nullable=False, server_default="common", index=True)
    binding: Mapped[str] = mapped_column(String(50), nullable=False, server_default="none", index=True)
    bound: Mapped[bool] = mapped_column(nullable=False, server_default="false", index=True)
    cargo_hold: Mapped[str] = mapped_column(String(50), nullable=False, server_default="cargo_hold", index=True)
    cargo_bay: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1", index=True)

    characters: Mapped[list[Character]] = relationship(secondary=character_items, back_populates="items")


class CharacterCrewSkillRelation(IdMixin, TimestampMixin, ActiveMixin, OwnedModelMixin, Base):
    __tablename__ = "character_crew_skill_relations"

    MAX_LEVEL: ClassVar[int] = 700

    name: Mapped[str | None] = mapped_column(String(255))
    display_name: Mapped[str | None] = mapped_column(String(255))
    character_id: Mapped[int] = mapped_column(ForeignKey("characters.id"), nullable=False, index=True)
    crew_skill_id: Mapped[int] = mapped_column(ForeignKey("crew_skills.id"), nullable=False, index=True)
    level: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
    skill_type: Mapped[str | None] = mapped_column(String(50))
    progress: Mapped[float] = mapped_column(Float, nullable=False, server_default="0")

    character: Mapped[Character] = relationship(back_populates="crew_skill_relations")
    crew_skill: Mapped[CrewSkill] = relationship("CrewSkill")

    @validates("level")
    def validate_level(self, key: str, level: int) -> int:
        if not 1 <= level <= self.MAX_LEVEL:
            raise ValueError(f"Crew skill level must be between 1 and {self.MAX_LEVEL}.")
        return level

    def derive_progress(self) -> float:
        return self.level / self.MAX_LEVEL * 100

    def sync_derived_fields(self) -> None:
        if self.crew_skill is not None:
            self.name = self.crew_skill.name
            self.skill_type = self.crew_skill.skill_type
        if self.character is not None and self.crew_skill is not None:
            self.display_name = f"{self.character.name} - {self.crew_skill.name}"
        self.progress = self.derive_progress()


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
