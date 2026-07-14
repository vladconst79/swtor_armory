import pytest

from app.models import Character, Guild, Title, Vehicle


def test_title_supports_expected_fields_and_values() -> None:
    title = Title(name="The Infernal", source="operation", type="legacy")

    assert title.source == "operation"
    assert title.type == "legacy"

    with pytest.raises(ValueError, match="Title source"):
        Title(name="Invalid", source="unknown")

    with pytest.raises(ValueError, match="Title type"):
        Title(name="Invalid", type="account")


def test_vehicle_supports_expected_fields_and_icon_url_metadata() -> None:
    vehicle = Vehicle(
        name="Avalanche Heavy Tank",
        source="operation",
        bind="bind_on_legacy",
        icon_url="https://example.com/icons/avalanche.png",
    )

    vehicle.sync_icon_metadata_from_url()

    assert vehicle.source == "operation"
    assert vehicle.bind == "bind_on_legacy"
    assert vehicle.icon_filename == "avalanche.png"
    assert Vehicle.ICON_STORAGE_MODE == "store_url_and_filename_metadata; fetch_binary_in_service"

    with pytest.raises(ValueError, match="Vehicle source"):
        Vehicle(name="Invalid", source="unknown")

    with pytest.raises(ValueError, match="Vehicle bind"):
        Vehicle(name="Invalid", bind="bind_on_account")

    with pytest.raises(ValueError, match="Vehicle icon URL"):
        Vehicle(name="Invalid", icon_url="https://example.com/file.txt")


def test_guild_syncs_member_count() -> None:
    guild = Guild(name="Republic Heroes")
    guild.characters = [
        Character(name="Vharen", faction="republic", owner_id=1),
        Character(name="Talan", faction="republic", owner_id=1),
    ]

    guild.sync_member_count()

    assert guild.member_count == 2


def test_free_text_character_guild_names_create_or_reuse_guild_records() -> None:
    character = Character(name="Vharen", faction="republic", owner_id=1, guild="Republic Heroes")
    existing_guilds: list[Guild] = []

    guild = Guild.find_or_create_from_character_guild(character, existing_guilds)

    assert guild is not None
    assert guild.name == "Republic Heroes"
    assert character.guild_record == guild
    assert existing_guilds == [guild]

    second_character = Character(name="Talan", faction="republic", owner_id=1, guild="Republic Heroes")
    reused_guild = Guild.find_or_create_from_character_guild(second_character, existing_guilds)

    assert reused_guild == guild
    assert existing_guilds == [guild]


def test_legacy_title_grants_to_all_current_user_characters() -> None:
    title = Title(name="The Infernal", type="legacy")
    characters = [
        Character(name="Vharen", faction="republic", owner_id=1),
        Character(name="Talan", faction="republic", owner_id=1),
    ]

    title.grant_to_characters(characters)

    assert characters[0].title_records == [title]
    assert characters[1].title_records == [title]


def test_character_title_does_not_auto_grant() -> None:
    title = Title(name="The Infernal", type="character")
    character = Character(name="Vharen", faction="republic", owner_id=1)

    title.grant_to_characters([character])

    assert character.title_records == []


def test_legacy_bound_vehicle_grants_to_all_current_user_characters() -> None:
    vehicle = Vehicle(name="Avalanche Heavy Tank", bind="bind_on_legacy")
    characters = [
        Character(name="Vharen", faction="republic", owner_id=1),
        Character(name="Talan", faction="republic", owner_id=1),
    ]

    vehicle.grant_to_characters(characters)

    assert characters[0].vehicle_records == [vehicle]
    assert characters[1].vehicle_records == [vehicle]


def test_non_legacy_bound_vehicle_does_not_auto_grant() -> None:
    vehicle = Vehicle(name="Avalanche Heavy Tank", bind="bind_on_pickup")
    character = Character(name="Vharen", faction="republic", owner_id=1)

    vehicle.grant_to_characters([character])

    assert character.vehicle_records == []
