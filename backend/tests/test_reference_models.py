from sqlalchemy import create_engine, inspect

from app.db.base import Base
from app.models import (
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
from app.models.user_owned import Character, CharacterCrewSkillRelation, Loadout, OperationLockout


REFERENCE_MODELS = [
    CrewSkill,
    Operation,
    OperationDifficulty,
    OperationBoss,
    OriginStory,
    ClassName,
    Role,
    Spec,
    Title,
    Vehicle,
    Guild,
]


def test_reference_models_are_registered_with_metadata() -> None:
    expected_tables = {
        "crew_skills",
        "operations",
        "operation_difficulties",
        "operation_bosses",
        "origin_stories",
        "class_names",
        "roles",
        "specs",
        "titles",
        "vehicles",
        "guilds",
    }

    assert expected_tables <= set(Base.metadata.tables)


def test_reference_models_have_shared_reference_fields() -> None:
    for model in REFERENCE_MODELS:
        columns = inspect(model).columns

        assert columns.id.primary_key is True
        assert columns.created_at.nullable is False
        assert columns.updated_at.nullable is False
        assert columns.active.nullable is False
        assert "owner_id" not in columns


def test_reference_tables_can_be_created() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")

    Base.metadata.create_all(bind=engine)

    table_names = set(inspect(engine).get_table_names())
    assert "crew_skills" in table_names
    assert "operation_bosses" in table_names
    assert "specs" in table_names
    assert "guilds" in table_names


def test_user_owned_reference_columns_now_have_foreign_keys() -> None:
    expected_foreign_keys = {
        Character: {
            "origin_story_id": "origin_stories.id",
            "guild_id": "guilds.id",
        },
        Loadout: {
            "role_id": "roles.id",
            "spec_id": "specs.id",
        },
        CharacterCrewSkillRelation: {
            "crew_skill_id": "crew_skills.id",
        },
        OperationLockout: {
            "boss_id": "operation_bosses.id",
            "operation_id": "operations.id",
            "difficulty_id": "operation_difficulties.id",
        },
    }

    for model, column_targets in expected_foreign_keys.items():
        columns = inspect(model).columns
        for column_name, target in column_targets.items():
            assert any(foreign_key.target_fullname == target for foreign_key in columns[column_name].foreign_keys)
