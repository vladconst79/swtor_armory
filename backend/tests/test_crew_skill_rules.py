import pytest

from app.models import Character, CrewSkill
from app.models.user_owned import CharacterCrewSkillRelation


def test_crew_skill_supports_expected_skill_types() -> None:
    CrewSkill(name="Armormech", skill_type="crafting")
    CrewSkill(name="Bioanalysis", skill_type="gathering")
    CrewSkill(name="Diplomacy", skill_type="mission")

    with pytest.raises(ValueError, match="crafting, gathering, mission"):
        CrewSkill(name="Invalid", skill_type="invalid")


def test_character_crew_skill_relation_validates_level_range() -> None:
    CharacterCrewSkillRelation(owner_id=1, level=1)
    CharacterCrewSkillRelation(owner_id=1, level=700)

    with pytest.raises(ValueError, match="Crew skill level must be between 1 and 700"):
        CharacterCrewSkillRelation(owner_id=1, level=0)

    with pytest.raises(ValueError, match="Crew skill level must be between 1 and 700"):
        CharacterCrewSkillRelation(owner_id=1, level=701)


def test_character_crew_skill_relation_derives_progress() -> None:
    relation = CharacterCrewSkillRelation(owner_id=1, level=350)

    assert relation.derive_progress() == 50


def test_character_crew_skill_relation_syncs_derived_fields() -> None:
    relation = CharacterCrewSkillRelation(
        owner_id=1,
        character=Character(name="Vharen", faction="republic", owner_id=1),
        crew_skill=CrewSkill(name="Bioanalysis", skill_type="gathering"),
        level=175,
    )

    relation.sync_derived_fields()

    assert relation.name == "Bioanalysis"
    assert relation.display_name == "Vharen - Bioanalysis"
    assert relation.skill_type == "gathering"
    assert relation.progress == 25


def test_crew_skill_related_skill_domain_matches_old_behavior() -> None:
    assert CrewSkill(name="Armormech", skill_type="crafting").related_skill_domain == ["gathering", "mission"]
    assert CrewSkill(name="Bioanalysis", skill_type="gathering").related_skill_domain == ["crafting"]
    assert CrewSkill(name="Diplomacy", skill_type="mission").related_skill_domain == ["crafting"]


def test_crew_skill_add_related_skill_keeps_relationship_bidirectional() -> None:
    crafting = CrewSkill(name="Armormech", skill_type="crafting")
    gathering = CrewSkill(name="Scavenging", skill_type="gathering")

    crafting.add_related_skill(gathering)

    assert crafting.related_skills == [gathering]
    assert gathering.related_skills == [crafting]


def test_crew_skill_related_skill_rules_use_hard_validation() -> None:
    crafting = CrewSkill(name="Armormech", skill_type="crafting")
    crafting.related_skills = [
        CrewSkill(name="Scavenging", skill_type="gathering"),
        CrewSkill(name="Underworld Trading", skill_type="mission"),
    ]
    crafting.validate_related_skill_rules()

    crafting.related_skills.append(CrewSkill(name="Bioanalysis", skill_type="gathering"))
    with pytest.raises(ValueError, match="no more than 2 related skills"):
        crafting.validate_related_skill_rules()

    gathering = CrewSkill(name="Slicing", skill_type="gathering")
    gathering.related_skills = [CrewSkill(name="Bioanalysis", skill_type="gathering")]
    with pytest.raises(ValueError, match="allowed skill type pairing"):
        gathering.validate_related_skill_rules()
