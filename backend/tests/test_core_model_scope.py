from sqlalchemy import CheckConstraint

from app.db.base import Base
from app.models import Character, CharacterCrewSkillRelation, Item, Loadout, OperationLockout


USER_OWNED_BUSINESS_TABLES = [
    Character.__table__,
    Loadout.__table__,
    Item.__table__,
    CharacterCrewSkillRelation.__table__,
    OperationLockout.__table__,
]


def test_stage_4_models_do_not_encode_business_rule_constraints() -> None:
    for table in USER_OWNED_BUSINESS_TABLES:
        assert not any(isinstance(constraint, CheckConstraint) for constraint in table.constraints)


def test_stage_4_metadata_is_structural_schema_only() -> None:
    business_rule_names = {
        "ck_characters_level_range",
        "ck_characters_valor_rank_range",
        "ck_items_cargo_bay_range",
        "ck_items_bound_personal_cargo",
        "ck_character_crew_skill_relations_level_range",
        "ck_operation_lockouts_unique_boss_difficulty_week",
    }

    constraint_names = {
        constraint.name
        for table in Base.metadata.tables.values()
        for constraint in table.constraints
        if constraint.name is not None
    }

    assert business_rule_names.isdisjoint(constraint_names)
