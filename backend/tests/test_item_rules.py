import pytest

from app.models import Item


def test_item_supports_expected_rarity_values() -> None:
    for rarity in ["common", "uncommon", "rare", "epic", "legendary"]:
        Item(name=f"{rarity} item", owner_id=1, rarity=rarity)

    with pytest.raises(ValueError, match="Item rarity must be one of"):
        Item(name="Invalid", owner_id=1, rarity="artifact")


def test_item_supports_expected_binding_values() -> None:
    for binding in ["none", "bind_on_pickup", "bind_on_equip", "bind_on_legacy"]:
        Item(name=f"{binding} item", owner_id=1, binding=binding)

    with pytest.raises(ValueError, match="Item binding must be one of"):
        Item(name="Invalid", owner_id=1, binding="bind_on_account")


def test_item_supports_expected_cargo_hold_values() -> None:
    for cargo_hold in ["cargo_hold", "cargo_hold_shared", "cargo_hold_guild"]:
        Item(name=f"{cargo_hold} item", owner_id=1, cargo_hold=cargo_hold)

    with pytest.raises(ValueError, match="Item cargo hold must be one of"):
        Item(name="Invalid", owner_id=1, cargo_hold="ship_bank")


def test_item_validates_cargo_bay_range() -> None:
    Item(name="First Bay", owner_id=1, cargo_bay=1)
    Item(name="Last Bay", owner_id=1, cargo_bay=8)

    with pytest.raises(ValueError, match="Cargo bay must be between 1 and 8"):
        Item(name="Too Low", owner_id=1, cargo_bay=0)

    with pytest.raises(ValueError, match="Cargo bay must be between 1 and 8"):
        Item(name="Too High", owner_id=1, cargo_bay=9)


def test_item_requires_bound_items_to_stay_in_personal_cargo_hold() -> None:
    Item(name="Bound Personal", owner_id=1, bound=True, cargo_hold="cargo_hold").validate_item_rules()

    with pytest.raises(ValueError, match="personal cargo hold"):
        Item(name="Bound Shared", owner_id=1, bound=True, cargo_hold="cargo_hold_shared").validate_item_rules()


def test_item_prevents_legacy_bound_items_in_guild_cargo_hold() -> None:
    Item(
        name="Legacy Shared",
        owner_id=1,
        binding="bind_on_legacy",
        cargo_hold="cargo_hold_shared",
    ).validate_item_rules()

    with pytest.raises(ValueError, match="guild cargo hold"):
        Item(
            name="Legacy Guild",
            owner_id=1,
            binding="bind_on_legacy",
            cargo_hold="cargo_hold_guild",
        ).validate_item_rules()
