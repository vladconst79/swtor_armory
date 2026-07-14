from sqlalchemy import create_engine, inspect

from app.db.base import Base
from app.models import Character, CharacterCrewSkillRelation, Item, Loadout, OperationLockout


USER_OWNED_MODELS = [
    Character,
    Loadout,
    Item,
    CharacterCrewSkillRelation,
    OperationLockout,
]


def test_user_owned_models_are_registered_with_metadata() -> None:
    assert "characters" in Base.metadata.tables
    assert "loadouts" in Base.metadata.tables
    assert "items" in Base.metadata.tables
    assert "character_crew_skill_relations" in Base.metadata.tables
    assert "operation_lockouts" in Base.metadata.tables


def test_user_owned_models_have_shared_owned_fields() -> None:
    for model in USER_OWNED_MODELS:
        columns = inspect(model).columns

        assert columns.id.primary_key is True
        assert columns.created_at.nullable is False
        assert columns.updated_at.nullable is False
        assert columns.active.nullable is False
        assert columns.owner_id.nullable is False
        assert any(foreign_key.target_fullname == "users.id" for foreign_key in columns.owner_id.foreign_keys)


def test_user_owned_tables_can_be_created() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")

    Base.metadata.create_all(bind=engine)

    table_names = inspect(engine).get_table_names()
    assert "characters" in table_names
    assert "loadouts" in table_names
    assert "items" in table_names
    assert "character_crew_skill_relations" in table_names
    assert "operation_lockouts" in table_names
