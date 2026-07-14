import pytest

from app.models import Character, ClassName, CrewSkill, Guild, Loadout, OriginStory, Role, Title, Vehicle
from app.models.user_owned import CharacterCrewSkillRelation


def make_character(**overrides: object) -> Character:
    values = {
        "name": "Vharen",
        "faction": "republic",
        "owner_id": 1,
    }
    values.update(overrides)
    return Character(**values)


def test_character_validates_level_range() -> None:
    make_character(level=1)
    make_character(level=80)

    with pytest.raises(ValueError, match="Level must be between 1 and 80"):
        make_character(level=0)

    with pytest.raises(ValueError, match="Level must be between 1 and 80"):
        make_character(level=81)


def test_character_validates_valor_rank_range() -> None:
    make_character(valor_rank=1)
    make_character(valor_rank=100)

    with pytest.raises(ValueError, match="Valor rank must be between 1 and 100"):
        make_character(valor_rank=0)

    with pytest.raises(ValueError, match="Valor rank must be between 1 and 100"):
        make_character(valor_rank=101)


def test_character_allows_no_more_than_two_class_names() -> None:
    character = make_character()
    character.class_names = [
        ClassName(name="Guardian", power_type="force"),
        ClassName(name="Sage", power_type="force"),
        ClassName(name="Sentinel", power_type="force"),
    ]

    with pytest.raises(ValueError, match="no more than 2 class names"):
        character.validate_character_rules()


def test_character_requires_class_names_to_match_origin_story_power_type() -> None:
    character = make_character()
    character.origin_story = OriginStory(name="Jedi Knight", power_type="force")
    character.class_names = [ClassName(name="Vanguard", power_type="tech")]

    with pytest.raises(ValueError, match="same power type"):
        character.validate_character_rules()


def test_character_allows_matching_class_name_power_types() -> None:
    character = make_character()
    character.origin_story = OriginStory(name="Jedi Knight", power_type="force")
    character.class_names = [ClassName(name="Guardian", power_type="force")]

    character.validate_character_rules()


def test_character_allows_no_more_than_three_crew_skills() -> None:
    character = make_character()
    character.crew_skill_relations = [
        CharacterCrewSkillRelation(owner_id=1, crew_skill=CrewSkill(name=f"Skill {index}", skill_type="gathering"))
        for index in range(4)
    ]

    with pytest.raises(ValueError, match="no more than 3 crew skills"):
        character.validate_character_rules()


def test_character_allows_no_more_than_one_crafting_crew_skill() -> None:
    character = make_character()
    character.crew_skill_relations = [
        CharacterCrewSkillRelation(owner_id=1, crew_skill=CrewSkill(name="Armormech", skill_type="crafting")),
        CharacterCrewSkillRelation(owner_id=1, skill_type="crafting"),
    ]

    with pytest.raises(ValueError, match="no more than 1 crafting crew skill"):
        character.validate_character_rules()


def test_character_allows_no_more_than_ten_loadouts() -> None:
    character = make_character()
    character.loadouts = [
        Loadout(name=f"Loadout {index}", loadout_type="pve", owner_id=1)
        for index in range(11)
    ]

    with pytest.raises(ValueError, match="no more than 10 loadouts"):
        character.validate_character_rules()


def test_character_derives_display_name_from_guild_record_or_free_text_guild() -> None:
    character = make_character(guild_record=Guild(name="Republic Heroes"))

    assert character.derive_display_name() == "[Republic Heroes] Vharen"

    character.guild_record = None
    character.guild = "Free Text Guild"
    assert character.derive_display_name() == "[Free Text Guild] Vharen"

    character.guild = None
    assert character.derive_display_name() == "Vharen"


def test_character_syncs_derived_counts_and_display_name() -> None:
    character = make_character(guild_record=Guild(name="Republic Heroes"))
    character.title_records = [Title(name="Conqueror"), Title(name="Liberator")]
    character.vehicle_records = [Vehicle(name="Speeder")]
    character.crew_skill_relations = [
        CharacterCrewSkillRelation(owner_id=1, crew_skill=CrewSkill(name="Bioanalysis", skill_type="gathering"))
    ]

    character.sync_derived_fields()

    assert character.display_name == "[Republic Heroes] Vharen"
    assert character.titles == 2
    assert character.mounts == 1
    assert character.crew_skills_count == 1


def test_character_derives_available_roles_from_selected_class_names() -> None:
    tank = Role(id=1, name="Tank")
    dps = Role(id=2, name="DPS")
    guardian = ClassName(name="Guardian", power_type="force")
    guardian.roles = [tank, dps]
    juggernaut = ClassName(name="Juggernaut", power_type="force")
    juggernaut.roles = [tank]
    character = make_character()
    character.class_names = [guardian, juggernaut]

    assert character.available_roles == [tank, dps]
