import base64

import pytest

from app.models import Character, ClassName, Loadout, Role, Spec


def parsely_url(build: str = "12312312") -> str:
    encoded_build = base64.b64encode(build.encode()).decode()
    return f"https://parsely.io/parser/combat-styles/jedi/{encoded_build}"


def test_loadout_supports_pve_and_pvp_types() -> None:
    Loadout(name="PvE Build", loadout_type="pve", owner_id=1)
    Loadout(name="PvP Build", loadout_type="pvp", owner_id=1)

    with pytest.raises(ValueError, match="pve or pvp"):
        Loadout(name="Invalid", loadout_type="solo", owner_id=1)


def test_loadout_validates_parsely_urls() -> None:
    Loadout(name="Valid", loadout_type="pve", owner_id=1, loadout_url=parsely_url())

    with pytest.raises(ValueError, match="valid Parsely combat style link"):
        Loadout(name="Bad Host", loadout_type="pve", owner_id=1, loadout_url="https://example.com/build")

    with pytest.raises(ValueError, match="valid Parsely combat style link"):
        Loadout(name="Bad Build", loadout_type="pve", owner_id=1, loadout_url=parsely_url("12345678"))


def test_loadout_derives_role_from_selected_spec() -> None:
    role = Role(id=7, name="DPS")
    spec = Spec(name="Vigilance", role=role, class_name=ClassName(name="Guardian", power_type="force"))
    loadout = Loadout(name="Build", loadout_type="pve", owner_id=1, spec=spec)

    loadout.sync_derived_fields()

    assert loadout.role == role
    assert loadout.role_id == 7


def test_loadout_uses_safe_preview_link_instead_of_iframe_html() -> None:
    url = parsely_url()
    loadout = Loadout(name="Build", loadout_type="pve", owner_id=1, loadout_url=url)

    loadout.sync_derived_fields()

    assert loadout.loadout_iframe == url
    assert "<iframe" not in loadout.loadout_iframe


def test_loadout_available_characters_match_spec_mirror_spec_and_role() -> None:
    dps = Role(id=1, name="DPS")
    tank = Role(id=2, name="Tank")
    guardian = ClassName(id=10, name="Guardian", power_type="force")
    juggernaut = ClassName(id=11, name="Juggernaut", power_type="force")
    vanguard = ClassName(id=12, name="Vanguard", power_type="tech")
    mirror_spec = Spec(name="Vengeance", role=dps, class_name=juggernaut)
    spec = Spec(name="Vigilance", role=dps, class_name=guardian, mirror_spec=mirror_spec)
    loadout = Loadout(name="Build", loadout_type="pve", owner_id=1, spec=spec)
    matching_primary = Character(name="Primary", faction="republic", owner_id=1)
    matching_primary.class_names = [guardian]
    matching_primary.roles = [dps]
    matching_mirror = Character(name="Mirror", faction="empire", owner_id=1)
    matching_mirror.class_names = [juggernaut]
    matching_mirror.roles = [dps]
    wrong_role = Character(name="Wrong Role", faction="republic", owner_id=1)
    wrong_role.class_names = [guardian]
    wrong_role.roles = [tank]
    wrong_class = Character(name="Wrong Class", faction="republic", owner_id=1)
    wrong_class.class_names = [vanguard]
    wrong_class.roles = [dps]

    assert loadout.available_characters([matching_primary, matching_mirror, wrong_role, wrong_class]) == [
        matching_primary,
        matching_mirror,
    ]
