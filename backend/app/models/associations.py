from sqlalchemy import Column, ForeignKey, Table

from app.db.base import Base


character_class_names = Table(
    "character_class_names",
    Base.metadata,
    Column("character_id", ForeignKey("characters.id"), primary_key=True),
    Column("class_name_id", ForeignKey("class_names.id"), primary_key=True),
)

character_roles = Table(
    "character_roles",
    Base.metadata,
    Column("character_id", ForeignKey("characters.id"), primary_key=True),
    Column("role_id", ForeignKey("roles.id"), primary_key=True),
)

character_loadouts = Table(
    "character_loadouts",
    Base.metadata,
    Column("character_id", ForeignKey("characters.id"), primary_key=True),
    Column("loadout_id", ForeignKey("loadouts.id"), primary_key=True),
)

character_items = Table(
    "character_items",
    Base.metadata,
    Column("character_id", ForeignKey("characters.id"), primary_key=True),
    Column("item_id", ForeignKey("items.id"), primary_key=True),
)

character_vehicles = Table(
    "character_vehicles",
    Base.metadata,
    Column("character_id", ForeignKey("characters.id"), primary_key=True),
    Column("vehicle_id", ForeignKey("vehicles.id"), primary_key=True),
)

character_titles = Table(
    "character_titles",
    Base.metadata,
    Column("character_id", ForeignKey("characters.id"), primary_key=True),
    Column("title_id", ForeignKey("titles.id"), primary_key=True),
)

class_name_roles = Table(
    "class_name_roles",
    Base.metadata,
    Column("class_name_id", ForeignKey("class_names.id"), primary_key=True),
    Column("role_id", ForeignKey("roles.id"), primary_key=True),
)

crew_skill_related_skills = Table(
    "crew_skill_related_skills",
    Base.metadata,
    Column("skill_id", ForeignKey("crew_skills.id"), primary_key=True),
    Column("related_skill_id", ForeignKey("crew_skills.id"), primary_key=True),
)

operation_difficulties = Table(
    "operation_difficulties_rel",
    Base.metadata,
    Column("operation_id", ForeignKey("operations.id"), primary_key=True),
    Column("difficulty_id", ForeignKey("operation_difficulties.id"), primary_key=True),
)
