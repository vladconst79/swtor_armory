from collections.abc import Generator

import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session, sessionmaker

from app.db.base import Base
from app.db.seed import OPERATIONS, SPEC_PAIRS, seed_reference_data
from app.models import (
    ClassName,
    CrewSkill,
    Operation,
    OperationBoss,
    OperationDifficulty,
    OriginStory,
    Role,
    Spec,
)


@pytest.fixture
def seed_session() -> Generator[Session, None, None]:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def scalar_count(session: Session, model: type[object]) -> int:
    return session.scalar(select(func.count()).select_from(model)) or 0


def test_seed_reference_data_populates_crew_skills(seed_session: Session) -> None:
    seed_reference_data(seed_session)

    assert scalar_count(seed_session, CrewSkill) == 14
    assert seed_session.scalar(select(CrewSkill).where(CrewSkill.name == "Armormech")).skill_type == "crafting"
    assert seed_session.scalar(select(CrewSkill).where(CrewSkill.name == "Bioanalysis")).skill_type == "gathering"
    assert seed_session.scalar(select(CrewSkill).where(CrewSkill.name == "Diplomacy")).skill_type == "mission"


def test_seed_reference_data_populates_operation_difficulties(seed_session: Session) -> None:
    seed_reference_data(seed_session)

    difficulties = {
        difficulty.name: difficulty.full_name
        for difficulty in seed_session.scalars(select(OperationDifficulty)).all()
    }
    assert difficulties == {
        "SM": "Story Mode",
        "VM": "Veteran Mode",
        "MM": "Master Mode",
    }


def test_seed_reference_data_populates_operations_and_bosses(seed_session: Session) -> None:
    seed_reference_data(seed_session)

    assert scalar_count(seed_session, Operation) == 12
    assert scalar_count(seed_session, OperationBoss) == sum(len(operation[3]) for operation in OPERATIONS)

    operation = seed_session.scalar(select(Operation).where(Operation.name == "Eternity Vault"))
    assert operation.short_name == "EV"
    assert [difficulty.name for difficulty in operation.difficulties] == ["SM", "VM"]
    assert [boss.name for boss in sorted(operation.bosses, key=lambda boss: boss.sequence)] == [
        "Ancient Pylons",
        "Gharj",
        "Annihilation Droid XRR-3",
        "Infernal Council",
        "Soa, the Infernal One",
    ]


def test_seed_reference_data_populates_origin_stories_classes_and_roles(seed_session: Session) -> None:
    seed_reference_data(seed_session)

    assert scalar_count(seed_session, OriginStory) == 8
    assert scalar_count(seed_session, ClassName) == 16
    assert scalar_count(seed_session, Role) == 3

    tank = seed_session.scalar(select(Role).where(Role.name == "Tank"))
    healer = seed_session.scalar(select(Role).where(Role.name == "Healer"))
    dps = seed_session.scalar(select(Role).where(Role.name == "DPS"))
    assert {class_name.name for class_name in tank.class_names} == {
        "Jedi Guardian",
        "Jedi Shadow",
        "Vanguard",
        "Sith Juggernaut",
        "Sith Assassin",
        "Powertech",
    }
    assert {class_name.name for class_name in healer.class_names} == {
        "Jedi Sage",
        "Scoundrel",
        "Commando",
        "Sith Sorcerer",
        "Operative",
        "Mercenary",
    }
    assert len(dps.class_names) == 16


def test_seed_reference_data_populates_specs_and_mirror_relationships(seed_session: Session) -> None:
    seed_reference_data(seed_session)

    assert scalar_count(seed_session, Spec) == len(SPEC_PAIRS) * 2

    tactics = seed_session.scalar(select(Spec).where(Spec.name == "Tactics"))
    advanced_prototype = seed_session.scalar(select(Spec).where(Spec.name == "Advanced Prototype"))
    assert tactics.class_name.name == "Vanguard"
    assert tactics.role.name == "DPS"
    assert tactics.mirror_spec == advanced_prototype
    assert advanced_prototype.mirror_spec == tactics


def test_seed_reference_data_is_idempotent(seed_session: Session) -> None:
    seed_reference_data(seed_session)
    first_counts = {
        CrewSkill: scalar_count(seed_session, CrewSkill),
        OperationDifficulty: scalar_count(seed_session, OperationDifficulty),
        Operation: scalar_count(seed_session, Operation),
        OperationBoss: scalar_count(seed_session, OperationBoss),
        OriginStory: scalar_count(seed_session, OriginStory),
        ClassName: scalar_count(seed_session, ClassName),
        Role: scalar_count(seed_session, Role),
        Spec: scalar_count(seed_session, Spec),
    }

    seed_reference_data(seed_session)

    assert {
        model: scalar_count(seed_session, model)
        for model in first_counts
    } == first_counts
