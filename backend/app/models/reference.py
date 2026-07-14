from typing import ClassVar

from sqlalchemy import ForeignKey, Integer, LargeBinary, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.db.base import Base
from app.models.associations import (
    character_class_names,
    character_roles,
    character_titles,
    character_vehicles,
    class_name_roles,
    crew_skill_related_skills,
    operation_difficulties,
)
from app.models.mixins import ActiveMixin, IdMixin, TimestampMixin


class CrewSkill(IdMixin, TimestampMixin, ActiveMixin, Base):
    __tablename__ = "crew_skills"

    ALLOWED_SKILL_TYPES: ClassVar[frozenset[str]] = frozenset({"crafting", "gathering", "mission"})
    MAX_RELATED_SKILLS_FOR_CRAFTING: ClassVar[int] = 2

    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    skill_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    related_skills: Mapped[list["CrewSkill"]] = relationship(
        "CrewSkill",
        secondary=crew_skill_related_skills,
        primaryjoin=lambda: CrewSkill.id == crew_skill_related_skills.c.skill_id,
        secondaryjoin=lambda: CrewSkill.id == crew_skill_related_skills.c.related_skill_id,
    )

    @validates("skill_type")
    def validate_skill_type(self, key: str, skill_type: str) -> str:
        if skill_type not in self.ALLOWED_SKILL_TYPES:
            allowed_values = ", ".join(sorted(self.ALLOWED_SKILL_TYPES))
            raise ValueError(f"Crew skill type must be one of: {allowed_values}.")
        return skill_type

    @property
    def related_skill_domain(self) -> list[str]:
        if self.skill_type == "crafting":
            return ["gathering", "mission"]
        return ["crafting"]

    def add_related_skill(self, related_skill: "CrewSkill") -> None:
        if related_skill not in self.related_skills:
            self.related_skills.append(related_skill)
        if self not in related_skill.related_skills:
            related_skill.related_skills.append(self)

    def validate_related_skill_rules(self) -> None:
        for related_skill in self.related_skills:
            if related_skill.skill_type not in self.related_skill_domain:
                raise ValueError("Related crew skills must match the allowed skill type pairing.")

        if self.skill_type == "crafting" and len(self.related_skills) > self.MAX_RELATED_SKILLS_FOR_CRAFTING:
            raise ValueError(
                f"Crafting crew skills can have no more than {self.MAX_RELATED_SKILLS_FOR_CRAFTING} related skills."
            )


class Operation(IdMixin, TimestampMixin, ActiveMixin, Base):
    __tablename__ = "operations"

    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    short_name: Mapped[str | None] = mapped_column(String(50), index=True)

    bosses: Mapped[list["OperationBoss"]] = relationship(back_populates="operation")
    difficulties: Mapped[list["OperationDifficulty"]] = relationship(
        secondary=operation_difficulties,
        back_populates="operations",
    )


class OperationDifficulty(IdMixin, TimestampMixin, ActiveMixin, Base):
    __tablename__ = "operation_difficulties"

    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    color: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")

    operations: Mapped[list[Operation]] = relationship(
        secondary=operation_difficulties,
        back_populates="difficulties",
    )


class OperationBoss(IdMixin, TimestampMixin, ActiveMixin, Base):
    __tablename__ = "operation_bosses"

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    sequence: Mapped[int] = mapped_column(Integer, nullable=False, server_default="10")
    operation_id: Mapped[int] = mapped_column(ForeignKey("operations.id"), nullable=False, index=True)

    operation: Mapped[Operation] = relationship(back_populates="bosses")


class OriginStory(IdMixin, TimestampMixin, ActiveMixin, Base):
    __tablename__ = "origin_stories"

    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    power_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)


class ClassName(IdMixin, TimestampMixin, ActiveMixin, Base):
    __tablename__ = "class_names"

    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    power_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    class_icon: Mapped[bytes | None] = mapped_column(LargeBinary)

    specs: Mapped[list["Spec"]] = relationship(back_populates="class_name")
    characters: Mapped[list["Character"]] = relationship(secondary=character_class_names, back_populates="class_names")
    roles: Mapped[list["Role"]] = relationship(secondary=class_name_roles, back_populates="class_names")


class Role(IdMixin, TimestampMixin, ActiveMixin, Base):
    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    color: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    icon: Mapped[bytes | None] = mapped_column(LargeBinary)

    specs: Mapped[list["Spec"]] = relationship(back_populates="role")
    characters: Mapped[list["Character"]] = relationship(secondary=character_roles, back_populates="roles")
    class_names: Mapped[list[ClassName]] = relationship(secondary=class_name_roles, back_populates="roles")


class Spec(IdMixin, TimestampMixin, ActiveMixin, Base):
    __tablename__ = "specs"

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), nullable=False, index=True)
    class_name_id: Mapped[int] = mapped_column(ForeignKey("class_names.id"), nullable=False, index=True)
    mirror_spec_id: Mapped[int | None] = mapped_column(ForeignKey("specs.id"), index=True)

    role: Mapped[Role] = relationship(back_populates="specs")
    class_name: Mapped[ClassName] = relationship(back_populates="specs")


class Title(IdMixin, TimestampMixin, ActiveMixin, Base):
    __tablename__ = "titles"

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    source: Mapped[str | None] = mapped_column(String(50), index=True)
    type: Mapped[str | None] = mapped_column(String(50), index=True)
    operation_id: Mapped[int | None] = mapped_column(ForeignKey("operations.id"), index=True)
    operation_difficulty_id: Mapped[int | None] = mapped_column(ForeignKey("operation_difficulties.id"), index=True)
    icon: Mapped[bytes | None] = mapped_column(LargeBinary)
    icon_filename: Mapped[str | None] = mapped_column(String(255))
    icon_url: Mapped[str | None] = mapped_column(String(2048))

    characters: Mapped[list["Character"]] = relationship(secondary=character_titles, back_populates="title_records")


class Vehicle(IdMixin, TimestampMixin, ActiveMixin, Base):
    __tablename__ = "vehicles"

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    source: Mapped[str | None] = mapped_column(String(50), index=True)
    bind: Mapped[str | None] = mapped_column(String(50), index=True)
    operation_id: Mapped[int | None] = mapped_column(ForeignKey("operations.id"), index=True)
    operation_difficulty_id: Mapped[int | None] = mapped_column(ForeignKey("operation_difficulties.id"), index=True)
    icon: Mapped[bytes | None] = mapped_column(LargeBinary)
    icon_filename: Mapped[str | None] = mapped_column(String(255))
    icon_url: Mapped[str | None] = mapped_column(String(2048))

    characters: Mapped[list["Character"]] = relationship(
        secondary=character_vehicles,
        back_populates="vehicle_records",
    )


class Guild(IdMixin, TimestampMixin, ActiveMixin, Base):
    __tablename__ = "guilds"

    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text)
    image: Mapped[bytes | None] = mapped_column(LargeBinary)
    guildmaster: Mapped[str | None] = mapped_column(String(255))
    member_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
