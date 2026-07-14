import base64
import re
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
from app.models.reference import (
    ClassName,
    CrewSkill,
    Guild,
    Operation,
    OperationBoss,
    OperationDifficulty,
    OriginStory,
    Role,
    Spec,
    Title,
    Vehicle,
)


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
    guild_record: Mapped[Guild | None] = relationship("Guild", back_populates="characters")
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

    ALLOWED_LOADOUT_TYPES: ClassVar[frozenset[str]] = frozenset({"pve", "pvp"})
    PARSELY_URL_PATTERN: ClassVar[re.Pattern[str]] = re.compile(
        r"^https://parsely\.io/parser/combat-styles/[a-z]+/[A-Za-z0-9+/=]+$"
    )
    PARSELY_BUILD_PATTERN: ClassVar[re.Pattern[str]] = re.compile(r"^[1-3]{8}$")

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    sequence: Mapped[int] = mapped_column(Integer, nullable=False, server_default="10")
    loadout_type: Mapped[str] = mapped_column(String(50), nullable=False)
    loadout_url: Mapped[str | None] = mapped_column(String(2048))
    loadout_iframe: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)
    role_id: Mapped[int | None] = mapped_column(ForeignKey("roles.id"), index=True)
    spec_id: Mapped[int | None] = mapped_column(ForeignKey("specs.id"), index=True)

    characters: Mapped[list[Character]] = relationship(secondary=character_loadouts, back_populates="loadouts")
    role: Mapped[Role | None] = relationship("Role")
    spec: Mapped[Spec | None] = relationship("Spec", foreign_keys=[spec_id])

    @validates("loadout_type")
    def validate_loadout_type(self, key: str, loadout_type: str) -> str:
        if loadout_type not in self.ALLOWED_LOADOUT_TYPES:
            raise ValueError("Loadout type must be either pve or pvp.")
        return loadout_type

    @validates("loadout_url")
    def validate_loadout_url(self, key: str, loadout_url: str | None) -> str | None:
        if loadout_url is not None and not self.is_valid_parsely_url(loadout_url):
            raise ValueError("Loadout URL must be a valid Parsely combat style link.")
        return loadout_url

    @classmethod
    def is_valid_parsely_url(cls, loadout_url: str) -> bool:
        if not cls.PARSELY_URL_PATTERN.match(loadout_url):
            return False

        encoded_build = loadout_url.rsplit("/", maxsplit=1)[-1]
        try:
            decoded_build = base64.b64decode(encoded_build, validate=True).decode()
        except (ValueError, UnicodeDecodeError):
            return False

        return bool(cls.PARSELY_BUILD_PATTERN.fullmatch(decoded_build))

    def derive_role(self) -> Role | None:
        return self.spec.role if self.spec is not None else None

    def derive_preview_url(self) -> str | None:
        return self.loadout_url

    def sync_derived_fields(self) -> None:
        role = self.derive_role()
        self.role = role
        self.role_id = role.id if role is not None else None
        self.loadout_iframe = self.derive_preview_url()

    def available_characters(self, characters: list[Character]) -> list[Character]:
        if self.spec is None:
            return []

        valid_class_names = [self.spec.class_name]
        if self.spec.mirror_spec is not None:
            valid_class_names.append(self.spec.mirror_spec.class_name)

        valid_class_name_keys = {
            class_name.id if class_name.id is not None else id(class_name)
            for class_name in valid_class_names
            if class_name is not None
        }
        role = self.derive_role()
        role_key = role.id if role is not None and role.id is not None else id(role)

        available_characters: list[Character] = []
        for character in characters:
            character_class_name_keys = {
                class_name.id if class_name.id is not None else id(class_name)
                for class_name in character.class_names
            }
            character_role_keys = {
                character_role.id if character_role.id is not None else id(character_role)
                for character_role in character.roles
            }
            if character_class_name_keys & valid_class_name_keys and role_key in character_role_keys:
                available_characters.append(character)

        return available_characters


class Item(IdMixin, TimestampMixin, ActiveMixin, OwnedModelMixin, Base):
    __tablename__ = "items"

    ALLOWED_RARITIES: ClassVar[frozenset[str]] = frozenset({"common", "uncommon", "rare", "epic", "legendary"})
    ALLOWED_BINDINGS: ClassVar[frozenset[str]] = frozenset(
        {"none", "bind_on_pickup", "bind_on_equip", "bind_on_legacy"}
    )
    ALLOWED_CARGO_HOLDS: ClassVar[frozenset[str]] = frozenset(
        {"cargo_hold", "cargo_hold_shared", "cargo_hold_guild"}
    )
    MAX_CARGO_BAY: ClassVar[int] = 8

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    rarity: Mapped[str] = mapped_column(String(50), nullable=False, default="common", server_default="common", index=True)
    binding: Mapped[str] = mapped_column(String(50), nullable=False, default="none", server_default="none", index=True)
    bound: Mapped[bool] = mapped_column(default=False, nullable=False, server_default="false", index=True)
    cargo_hold: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="cargo_hold",
        server_default="cargo_hold",
        index=True,
    )
    cargo_bay: Mapped[int] = mapped_column(Integer, nullable=False, default=1, server_default="1", index=True)

    characters: Mapped[list[Character]] = relationship(secondary=character_items, back_populates="items")

    @validates("rarity")
    def validate_rarity(self, key: str, rarity: str) -> str:
        if rarity not in self.ALLOWED_RARITIES:
            allowed_values = ", ".join(sorted(self.ALLOWED_RARITIES))
            raise ValueError(f"Item rarity must be one of: {allowed_values}.")
        return rarity

    @validates("binding")
    def validate_binding(self, key: str, binding: str) -> str:
        if binding not in self.ALLOWED_BINDINGS:
            allowed_values = ", ".join(sorted(self.ALLOWED_BINDINGS))
            raise ValueError(f"Item binding must be one of: {allowed_values}.")
        return binding

    @validates("cargo_hold")
    def validate_cargo_hold(self, key: str, cargo_hold: str) -> str:
        if cargo_hold not in self.ALLOWED_CARGO_HOLDS:
            allowed_values = ", ".join(sorted(self.ALLOWED_CARGO_HOLDS))
            raise ValueError(f"Item cargo hold must be one of: {allowed_values}.")
        return cargo_hold

    @validates("cargo_bay")
    def validate_cargo_bay(self, key: str, cargo_bay: int) -> int:
        if not 1 <= cargo_bay <= self.MAX_CARGO_BAY:
            raise ValueError(f"Cargo bay must be between 1 and {self.MAX_CARGO_BAY}.")
        return cargo_bay

    def validate_item_rules(self) -> None:
        rarity = self.rarity or "common"
        binding = self.binding or "none"
        cargo_hold = self.cargo_hold or "cargo_hold"
        cargo_bay = self.cargo_bay or 1

        self.validate_rarity("rarity", rarity)
        self.validate_binding("binding", binding)
        self.validate_cargo_hold("cargo_hold", cargo_hold)
        self.validate_cargo_bay("cargo_bay", cargo_bay)

        if self.bound and cargo_hold != "cargo_hold":
            raise ValueError("Bound items must be stored in personal cargo hold.")

        if binding == "bind_on_legacy" and cargo_hold == "cargo_hold_guild":
            raise ValueError("Legacy-bound items cannot be stored in guild cargo hold.")


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
    boss: Mapped[OperationBoss] = relationship("OperationBoss")
    operation: Mapped[Operation] = relationship("Operation")
    difficulty: Mapped[OperationDifficulty] = relationship("OperationDifficulty")

    @staticmethod
    def reset_week_for(day: date) -> date:
        days_since_tuesday = (day.weekday() - 1) % 7
        return day.fromordinal(day.toordinal() - days_since_tuesday)

    @staticmethod
    def reset_week_end(reset_week: date) -> date:
        return reset_week.fromordinal(reset_week.toordinal() + 6)

    @classmethod
    def current_week_filter(cls, today: date) -> tuple[date, date]:
        reset_week = cls.reset_week_for(today)
        return reset_week, cls.reset_week_end(reset_week)

    @classmethod
    def filter_current_week(cls, lockouts: list["OperationLockout"], today: date) -> list["OperationLockout"]:
        week_start, week_end = cls.current_week_filter(today)
        return [lockout for lockout in lockouts if lockout.week is not None and week_start <= lockout.week <= week_end]

    @staticmethod
    def sort_by_week_descending(lockouts: list["OperationLockout"]) -> list["OperationLockout"]:
        return sorted(lockouts, key=lambda lockout: lockout.week or date.min, reverse=True)

    def derive_name(self) -> str | None:
        if self.operation is None or self.difficulty is None or self.week is None:
            return None

        week_start = self.reset_week_for(self.week)
        week_end = self.reset_week_end(week_start)
        return f"{self.operation.name} - {self.difficulty.name} - {week_start} - {week_end}"

    def derive_faction(self) -> str | None:
        return self.character.faction if self.character is not None else None

    def derive_completion_rate(self) -> float:
        if self.boss is None or self.boss.operation is None:
            return 0.0

        bosses = self.boss.operation.bosses
        if not bosses:
            return 0.0

        completed_bosses = [boss for boss in bosses if boss.sequence <= self.boss.sequence]
        return len(completed_bosses) / len(bosses) * 100

    def sync_derived_fields(self) -> None:
        self.name = self.derive_name()
        self.faction = self.derive_faction()
        self.completion_rate = self.derive_completion_rate()

    def duplicate_key(self) -> tuple[int | None, int | None, int | None, date | None]:
        character_id = self.character_id or (self.character.id if self.character is not None else None)
        boss_id = self.boss_id or (self.boss.id if self.boss is not None else None)
        difficulty_id = self.difficulty_id or (self.difficulty.id if self.difficulty is not None else None)
        return character_id, boss_id, difficulty_id, self.week

    def validate_unique_lockout(self, existing_lockouts: list["OperationLockout"]) -> None:
        own_key = self.duplicate_key()
        for lockout in existing_lockouts:
            if lockout is not self and lockout.duplicate_key() == own_key:
                raise ValueError("Character already has a lockout for this boss, difficulty, and week.")
