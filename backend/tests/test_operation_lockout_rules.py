from datetime import date

import pytest

from app.models import Character, Operation, OperationBoss, OperationDifficulty, OperationLockout


def make_operation_with_bosses() -> tuple[Operation, list[OperationBoss]]:
    operation = Operation(id=1, name="Eternity Vault")
    bosses = [
        OperationBoss(id=1, name="Annihilation Droid XRR-3", sequence=10, operation=operation),
        OperationBoss(id=2, name="Gharj", sequence=20, operation=operation),
        OperationBoss(id=3, name="Soa", sequence=30, operation=operation),
    ]
    operation.bosses = bosses
    return operation, bosses


def test_operation_models_expose_stage_9_fields() -> None:
    operation = Operation(name="Karagga's Palace", short_name="KP")
    difficulty = OperationDifficulty(name="SM", full_name="Story Mode", color=2)
    boss = OperationBoss(name="Bonethrasher", sequence=10, operation=operation)
    lockout = OperationLockout(
        owner_id=1,
        character=Character(name="Vharen", faction="republic", owner_id=1),
        operation=operation,
        difficulty=difficulty,
        boss=boss,
        week=date(2026, 7, 14),
    )

    assert operation.short_name == "KP"
    assert difficulty.full_name == "Story Mode"
    assert difficulty.color == 2
    assert boss.sequence == 10
    assert lockout.week == date(2026, 7, 14)


def test_operation_lockouts_sort_by_week_descending() -> None:
    older = OperationLockout(owner_id=1, week=date(2026, 7, 7))
    newer = OperationLockout(owner_id=1, week=date(2026, 7, 14))

    assert OperationLockout.sort_by_week_descending([older, newer]) == [newer, older]


def test_operation_lockout_derives_name_from_operation_difficulty_and_reset_week() -> None:
    operation, bosses = make_operation_with_bosses()
    difficulty = OperationDifficulty(name="SM", full_name="Story Mode")
    lockout = OperationLockout(
        owner_id=1,
        operation=operation,
        difficulty=difficulty,
        boss=bosses[0],
        week=date(2026, 7, 16),
    )

    assert lockout.derive_name() == "Eternity Vault - SM - 2026-07-14 - 2026-07-20"


def test_operation_lockout_derives_faction_from_character() -> None:
    lockout = OperationLockout(
        owner_id=1,
        character=Character(name="Vharen", faction="empire", owner_id=1),
    )

    assert lockout.derive_faction() == "empire"


def test_operation_lockout_derives_completion_rate_from_boss_sequence() -> None:
    operation, bosses = make_operation_with_bosses()
    lockout = OperationLockout(owner_id=1, boss=bosses[1], operation=operation)

    assert lockout.derive_completion_rate() == pytest.approx(66.6666666667)


def test_operation_lockout_syncs_derived_fields() -> None:
    operation, bosses = make_operation_with_bosses()
    difficulty = OperationDifficulty(name="VM", full_name="Veteran Mode")
    character = Character(name="Vharen", faction="republic", owner_id=1)
    lockout = OperationLockout(
        owner_id=1,
        character=character,
        operation=operation,
        difficulty=difficulty,
        boss=bosses[2],
        week=date(2026, 7, 14),
    )

    lockout.sync_derived_fields()

    assert lockout.name == "Eternity Vault - VM - 2026-07-14 - 2026-07-20"
    assert lockout.faction == "republic"
    assert lockout.completion_rate == 100


def test_operation_lockout_enforces_unique_character_boss_difficulty_week() -> None:
    character = Character(id=1, name="Vharen", faction="republic", owner_id=1)
    boss = OperationBoss(id=2, name="Gharj", sequence=20, operation=Operation(id=1, name="Eternity Vault"))
    difficulty = OperationDifficulty(id=3, name="SM", full_name="Story Mode")
    existing = OperationLockout(
        owner_id=1,
        character=character,
        boss=boss,
        difficulty=difficulty,
        week=date(2026, 7, 14),
    )
    duplicate = OperationLockout(
        owner_id=1,
        character=character,
        boss=boss,
        difficulty=difficulty,
        week=date(2026, 7, 14),
    )

    with pytest.raises(ValueError, match="already has a lockout"):
        duplicate.validate_unique_lockout([existing])


def test_operation_lockout_current_week_filter_uses_tuesday_reset() -> None:
    previous = OperationLockout(owner_id=1, week=date(2026, 7, 13))
    current_start = OperationLockout(owner_id=1, week=date(2026, 7, 14))
    current_end = OperationLockout(owner_id=1, week=date(2026, 7, 20))
    next_week = OperationLockout(owner_id=1, week=date(2026, 7, 21))

    assert OperationLockout.current_week_filter(date(2026, 7, 16)) == (date(2026, 7, 14), date(2026, 7, 20))
    assert OperationLockout.filter_current_week(
        [previous, current_start, current_end, next_week],
        today=date(2026, 7, 16),
    ) == [current_start, current_end]
