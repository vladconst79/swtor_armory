from sqlalchemy import create_engine, inspect

from app.db.base import Base
from app.models import Character, ClassName, CrewSkill, Operation, Role


ASSOCIATION_TABLES = {
    "character_class_names": {
        "character_id": "characters.id",
        "class_name_id": "class_names.id",
    },
    "character_roles": {
        "character_id": "characters.id",
        "role_id": "roles.id",
    },
    "character_loadouts": {
        "character_id": "characters.id",
        "loadout_id": "loadouts.id",
    },
    "character_items": {
        "character_id": "characters.id",
        "item_id": "items.id",
    },
    "character_vehicles": {
        "character_id": "characters.id",
        "vehicle_id": "vehicles.id",
    },
    "character_titles": {
        "character_id": "characters.id",
        "title_id": "titles.id",
    },
    "class_name_roles": {
        "class_name_id": "class_names.id",
        "role_id": "roles.id",
    },
    "crew_skill_related_skills": {
        "skill_id": "crew_skills.id",
        "related_skill_id": "crew_skills.id",
    },
    "operation_difficulties_rel": {
        "operation_id": "operations.id",
        "difficulty_id": "operation_difficulties.id",
    },
}


def test_association_tables_are_registered_with_metadata() -> None:
    assert set(ASSOCIATION_TABLES) <= set(Base.metadata.tables)


def test_association_tables_have_composite_primary_keys_and_foreign_keys() -> None:
    for table_name, expected_targets in ASSOCIATION_TABLES.items():
        table = Base.metadata.tables[table_name]

        assert {column.name for column in table.primary_key.columns} == set(expected_targets)
        for column_name, target in expected_targets.items():
            assert any(foreign_key.target_fullname == target for foreign_key in table.c[column_name].foreign_keys)


def test_association_tables_can_be_created() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")

    Base.metadata.create_all(bind=engine)

    assert set(ASSOCIATION_TABLES) <= set(inspect(engine).get_table_names())


def test_association_relationships_are_mapped() -> None:
    character_relationships = inspect(Character).relationships
    class_name_relationships = inspect(ClassName).relationships
    role_relationships = inspect(Role).relationships

    assert character_relationships.class_names.secondary.name == "character_class_names"
    assert character_relationships.roles.secondary.name == "character_roles"
    assert character_relationships.loadouts.secondary.name == "character_loadouts"
    assert character_relationships["items"].secondary.name == "character_items"
    assert character_relationships.vehicle_records.secondary.name == "character_vehicles"
    assert character_relationships.title_records.secondary.name == "character_titles"
    assert class_name_relationships.roles.secondary.name == "class_name_roles"
    assert role_relationships.class_names.secondary.name == "class_name_roles"
    assert inspect(CrewSkill).relationships.related_skills.secondary.name == "crew_skill_related_skills"
    assert inspect(Operation).relationships.difficulties.secondary.name == "operation_difficulties_rel"
