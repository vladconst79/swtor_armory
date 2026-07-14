from collections.abc import Iterable
from typing import TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

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

T = TypeVar("T")


CREW_SKILLS: dict[str, str] = {
    "Armormech": "crafting",
    "ArmsTech": "crafting",
    "Artifice": "crafting",
    "Biochem": "crafting",
    "Cybertech": "crafting",
    "Synthweaving": "crafting",
    "Slicing": "gathering",
    "Scavenging": "gathering",
    "Bioanalysis": "gathering",
    "Archaeology": "gathering",
    "Underworld Trading": "mission",
    "Diplomacy": "mission",
    "Investigation": "mission",
    "Treasure Hunting": "mission",
}

OPERATION_DIFFICULTIES: dict[str, str] = {
    "SM": "Story Mode",
    "VM": "Veteran Mode",
    "MM": "Master Mode",
}

OPERATIONS: list[tuple[str, str, list[str], list[str]]] = [
    (
        "Eternity Vault",
        "EV",
        ["SM", "VM"],
        ["Ancient Pylons", "Gharj", "Annihilation Droid XRR-3", "Infernal Council", "Soa, the Infernal One"],
    ),
    (
        "Karagga's Palace",
        "KP",
        ["SM", "VM"],
        ["Bonethrasher", "Jarg & Sorno", "Foreman Crusher", "G4-B3 Heavy Fabricator", "Karagga the Unyielding"],
    ),
    (
        "Explosive Conflict",
        "EC",
        ["SM", "VM", "MM"],
        ["Zorn & Toth", "Firebrand & Stormcaller", "Colonel Vorgath", "Warlord Kephess"],
    ),
    (
        "Terror From Beyond",
        "TFB",
        ["SM", "VM", "MM"],
        ["Writhing Horror", "Dread Guards", "Operator IX", "Kephess the Undying", "Terror From Beyond"],
    ),
    (
        "Scum and Villainy",
        "SV",
        ["SM", "VM", "MM"],
        [
            "Dash'roode",
            "Titan 6",
            "Thrasher",
            "Operations Chief",
            "Olok the Shadow",
            "Cartel Warlords",
            "Dread Master Styrak",
        ],
    ),
    (
        "Dread Fortress",
        "DF",
        ["SM", "VM", "MM"],
        [
            "Nefra, Who Bars the Way",
            "Gate Commander Draxus",
            "Grob'Thok, Who Feeds the Forge",
            "Corruptor Zero",
            "Dread Master Brontes",
        ],
    ),
    (
        "Dread Palace",
        "DP",
        ["SM", "VM", "MM"],
        [
            "Dread Master Bestia",
            "Dread Master Tyrans",
            "Dread Master Calphayus",
            "Dread Master Raptus",
            "Dread Council",
        ],
    ),
    (
        "The Ravagers",
        "Rav",
        ["SM", "VM"],
        ["Sparky", "Bulo", "Torque", "Blaster & Master", "Cortanni"],
    ),
    (
        "Temple of Sacrifice",
        "ToS",
        ["SM", "VM"],
        ["Malaphar the Savage", "Sword Squadron", "The Underlurker", "Revanite Commanders", "Revan"],
    ),
    (
        "Gods From the Machine",
        "GftM",
        ["SM", "VM", "MM"],
        [
            "Tyth, God of Rage",
            "Aivela & Esne",
            "Nahut, God of Rage",
            "Scyva, Mother of Sorrows",
            "Izax, The Ultimate Devourer",
        ],
    ),
    (
        "The Nature of Progress",
        "Dxun",
        ["SM", "VM", "MM"],
        [
            "The Pack Leader",
            "Breach CI-004: Lights Out",
            "Breacher CI-004: Fire Support",
            "Mutant Trandoshan Squad",
            "The Huntmaster",
            "Apex Vanguard",
        ],
    ),
    (
        "R-4 Anomaly",
        "R4",
        ["SM", "VM"],
        ["IP-CPT", "Watchdog", "Lady Dominique", "Lord Kanoth"],
    ),
]

ORIGIN_STORIES: dict[str, str] = {
    "Jedi Knight": "force",
    "Jedi Consular": "force",
    "Smuggler": "tech",
    "Trooper": "tech",
    "Sith Warrior": "force",
    "Sith Inquisitor": "force",
    "Bounty Hunter": "tech",
    "Imperial Agent": "tech",
}

CLASS_NAMES: dict[str, str] = {
    "Jedi Guardian": "force",
    "Jedi Sentinel": "force",
    "Jedi Sage": "force",
    "Jedi Shadow": "force",
    "Gunslinger": "tech",
    "Scoundrel": "tech",
    "Commando": "tech",
    "Vanguard": "tech",
    "Sith Juggernaut": "force",
    "Sith Marauder": "force",
    "Sith Sorcerer": "force",
    "Sith Assassin": "force",
    "Sniper": "tech",
    "Operative": "tech",
    "Mercenary": "tech",
    "Powertech": "tech",
}

ROLE_CLASS_NAMES: dict[str, list[str]] = {
    "Tank": [
        "Jedi Guardian",
        "Jedi Shadow",
        "Vanguard",
        "Sith Juggernaut",
        "Sith Assassin",
        "Powertech",
    ],
    "Healer": ["Jedi Sage", "Scoundrel", "Commando", "Sith Sorcerer", "Operative", "Mercenary"],
    "DPS": list(CLASS_NAMES),
}

SPEC_PAIRS: list[tuple[tuple[str, str, str], tuple[str, str, str]]] = [
    (("Advanced Prototype", "Powertech", "DPS"), ("Tactics", "Vanguard", "DPS")),
    (("Annihilation", "Sith Marauder", "DPS"), ("Watchman", "Jedi Sentinel", "DPS")),
    (("Arsenal", "Mercenary", "DPS"), ("Gunnery", "Commando", "DPS")),
    (("Bodyguard", "Mercenary", "Healer"), ("Combat Medic", "Commando", "Healer")),
    (("Carnage", "Sith Marauder", "DPS"), ("Combat", "Jedi Sentinel", "DPS")),
    (("Concealment", "Operative", "DPS"), ("Scrapper", "Scoundrel", "DPS")),
    (("Corruption", "Sith Sorcerer", "Healer"), ("Seer", "Jedi Sage", "Healer")),
    (("Darkness", "Sith Assassin", "Tank"), ("Kinetic Combat", "Jedi Shadow", "Tank")),
    (("Deception", "Sith Assassin", "DPS"), ("Infiltration", "Jedi Shadow", "DPS")),
    (("Engineering", "Sniper", "DPS"), ("Saboteur", "Gunslinger", "DPS")),
    (("Fury", "Sith Marauder", "DPS"), ("Concentration", "Jedi Sentinel", "DPS")),
    (("Hatred", "Sith Assassin", "DPS"), ("Serenity", "Jedi Shadow", "DPS")),
    (("Immortal", "Sith Juggernaut", "Tank"), ("Defense", "Jedi Guardian", "Tank")),
    (("Innovative Ordnance", "Mercenary", "DPS"), ("Assault Specialist", "Commando", "DPS")),
    (("Letality", "Operative", "DPS"), ("Ruffian", "Scoundrel", "DPS")),
    (("Lightning", "Sith Sorcerer", "DPS"), ("Telekinetics", "Jedi Sage", "DPS")),
    (("Madness", "Sith Sorcerer", "DPS"), ("Balance", "Jedi Sage", "DPS")),
    (("Marksmanship", "Sniper", "DPS"), ("Sharpshooter", "Gunslinger", "DPS")),
    (("Medicine", "Operative", "Healer"), ("Sawbones", "Scoundrel", "Healer")),
    (("Pyrotech", "Powertech", "DPS"), ("Plasmatech", "Vanguard", "DPS")),
    (("Rage", "Sith Juggernaut", "DPS"), ("Focus", "Jedi Guardian", "DPS")),
    (("Shield Tech", "Powertech", "Tank"), ("Shield Specialist", "Vanguard", "Tank")),
    (("Vengeance", "Sith Juggernaut", "DPS"), ("Vigilance", "Jedi Guardian", "DPS")),
    (("Virulence", "Sniper", "DPS"), ("Dirty Fighting", "Gunslinger", "DPS")),
]


def seed_reference_data(session: Session) -> None:
    crew_skills = _seed_named_typed_records(session, CrewSkill, CREW_SKILLS, "skill_type")
    difficulties = _seed_named_records(session, OperationDifficulty, OPERATION_DIFFICULTIES, "full_name")
    operations = _seed_operations(session, difficulties)
    origin_stories = _seed_named_typed_records(session, OriginStory, ORIGIN_STORIES, "power_type")
    class_names = _seed_named_typed_records(session, ClassName, CLASS_NAMES, "power_type")
    roles = _seed_roles(session, class_names)
    _seed_specs(session, class_names, roles)

    # Keep references alive for type checkers and future debugging hooks.
    _ = crew_skills, operations, origin_stories
    session.commit()


def _get_by_name(session: Session, model: type[T], name: str) -> T | None:
    return session.scalar(select(model).where(model.name == name))


def _seed_named_typed_records(
    session: Session,
    model: type[T],
    values: dict[str, str],
    attribute_name: str,
) -> dict[str, T]:
    records: dict[str, T] = {}
    for name, value in values.items():
        record = _get_by_name(session, model, name)
        if record is None:
            record = model(name=name, **{attribute_name: value})
            session.add(record)
        else:
            setattr(record, attribute_name, value)
        records[name] = record
    session.flush()
    return records


def _seed_named_records(
    session: Session,
    model: type[T],
    values: dict[str, str],
    attribute_name: str,
) -> dict[str, T]:
    return _seed_named_typed_records(session, model, values, attribute_name)


def _seed_operations(session: Session, difficulties: dict[str, OperationDifficulty]) -> dict[str, Operation]:
    operations: dict[str, Operation] = {}
    for operation_name, short_name, difficulty_names, boss_names in OPERATIONS:
        operation = _get_by_name(session, Operation, operation_name)
        if operation is None:
            operation = Operation(name=operation_name, short_name=short_name)
            session.add(operation)
        else:
            operation.short_name = short_name

        operation.difficulties = [difficulties[name] for name in difficulty_names]
        session.flush()
        _seed_operation_bosses(session, operation, boss_names)
        operations[operation_name] = operation
    session.flush()
    return operations


def _seed_operation_bosses(session: Session, operation: Operation, boss_names: Iterable[str]) -> None:
    existing_bosses = {boss.name: boss for boss in operation.bosses}
    for sequence, boss_name in enumerate(boss_names, start=1):
        boss = existing_bosses.get(boss_name)
        if boss is None:
            session.add(OperationBoss(name=boss_name, operation=operation, sequence=sequence))
        else:
            boss.sequence = sequence


def _seed_roles(session: Session, class_names: dict[str, ClassName]) -> dict[str, Role]:
    roles: dict[str, Role] = {}
    for role_name, role_class_names in ROLE_CLASS_NAMES.items():
        role = _get_by_name(session, Role, role_name)
        if role is None:
            role = Role(name=role_name)
            session.add(role)
        role.class_names = [class_names[class_name] for class_name in role_class_names]
        roles[role_name] = role
    session.flush()
    return roles


def _seed_specs(session: Session, class_names: dict[str, ClassName], roles: dict[str, Role]) -> None:
    spec_records: dict[str, Spec] = {}
    for left_spec, right_spec in SPEC_PAIRS:
        for spec_name, class_name, role_name in (left_spec, right_spec):
            spec = _get_by_name(session, Spec, spec_name)
            if spec is None:
                spec = Spec(name=spec_name, class_name=class_names[class_name], role=roles[role_name])
                session.add(spec)
            else:
                spec.class_name = class_names[class_name]
                spec.role = roles[role_name]
            spec_records[spec_name] = spec
    session.flush()

    for left_spec, right_spec in SPEC_PAIRS:
        left_name = left_spec[0]
        right_name = right_spec[0]
        spec_records[left_name].mirror_spec_id = spec_records[right_name].id
        spec_records[right_name].mirror_spec_id = spec_records[left_name].id
