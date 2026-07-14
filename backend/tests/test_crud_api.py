from collections.abc import Generator
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.security import create_access_token, get_password_hash
from app.db.base import Base
from app.db.seed import seed_reference_data
from app.db.session import get_db
from app.main import app
from app.models import Character, CrewSkill, Item, Loadout, OriginStory, Role, User


@pytest.fixture
def api_db() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        db.add_all(
            [
                User(
                    username="admin",
                    hashed_password=get_password_hash("secret"),
                    is_active=True,
                    is_swtor_admin=True,
                ),
                User(
                    username="normal",
                    hashed_password=get_password_hash("secret"),
                    is_active=True,
                    is_swtor_admin=False,
                ),
                User(
                    username="other",
                    hashed_password=get_password_hash("secret"),
                    is_active=True,
                    is_swtor_admin=False,
                ),
            ]
        )
        db.commit()
        seed_reference_data(db)
        yield db
    finally:
        db.close()


@pytest.fixture
def api_client(api_db: Session) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        yield api_db

    app.dependency_overrides[get_db] = override_get_db
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


def auth_headers(user_id: int) -> dict[str, str]:
    return {"Authorization": f"Bearer {create_access_token(subject=str(user_id))}"}


def test_reference_list_supports_pagination_sorting_and_filtering(api_client: TestClient) -> None:
    raw_filter = quote('{"name":"bio"}')

    response = api_client.get(
        f"/api/crew-skills?page=1&per_page=5&sort=name&order=desc&filter={raw_filter}",
        headers=auth_headers(2),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert [record["name"] for record in body["data"]] == ["Biochem", "Bioanalysis"]


def test_lookup_endpoint_returns_compact_reference_data(api_client: TestClient) -> None:
    response = api_client.get("/api/lookups/specs?q=Tactics", headers=auth_headers(2))

    assert response.status_code == 200
    assert response.json()["data"] == [{"id": 2, "name": "Tactics"}]


def test_admin_can_create_and_update_reference_data(api_client: TestClient, api_db: Session) -> None:
    create_response = api_client.post(
        "/api/crew-skills",
        json={"name": "Reverse Engineering", "skill_type": "mission"},
        headers=auth_headers(1),
    )
    assert create_response.status_code == 201
    crew_skill_id = create_response.json()["id"]

    update_response = api_client.patch(
        f"/api/crew-skills/{crew_skill_id}",
        json={"skill_type": "gathering"},
        headers=auth_headers(1),
    )

    assert update_response.status_code == 200
    assert update_response.json()["skill_type"] == "gathering"
    assert api_db.get(CrewSkill, crew_skill_id).skill_type == "gathering"


def test_normal_user_cannot_write_reference_data(api_client: TestClient) -> None:
    response = api_client.post(
        "/api/crew-skills",
        json={"name": "Forbidden Skill", "skill_type": "mission"},
        headers=auth_headers(2),
    )

    assert response.status_code == 403


def test_user_owned_crud_is_owner_scoped(api_client: TestClient, api_db: Session) -> None:
    origin_story = api_db.scalar(select(OriginStory).where(OriginStory.name == "Jedi Knight"))

    create_response = api_client.post(
        "/api/characters",
        json={
            "name": "Vharen",
            "faction": "republic",
            "origin_story_id": origin_story.id,
            "level": 80,
        },
        headers=auth_headers(2),
    )

    assert create_response.status_code == 201
    body = create_response.json()
    assert body["owner_id"] == 2
    assert body["display_name"] == "Vharen"
    character_id = body["id"]

    list_response = api_client.get("/api/characters", headers=auth_headers(2))
    assert list_response.status_code == 200
    assert list_response.json()["total"] == 1

    other_user_response = api_client.get(f"/api/characters/{character_id}", headers=auth_headers(3))
    assert other_user_response.status_code == 403

    other_user_update_response = api_client.patch(
        f"/api/characters/{character_id}",
        json={"server": "Star Forge"},
        headers=auth_headers(3),
    )
    assert other_user_update_response.status_code == 403

    other_user_delete_response = api_client.delete(f"/api/characters/{character_id}", headers=auth_headers(3))
    assert other_user_delete_response.status_code == 403

    update_response = api_client.patch(
        f"/api/characters/{character_id}",
        json={"server": "Darth Malgus"},
        headers=auth_headers(2),
    )
    assert update_response.status_code == 200
    assert update_response.json()["server"] == "Darth Malgus"


def test_admin_can_read_other_users_records(api_client: TestClient, api_db: Session) -> None:
    api_db.add(Character(name="Talan", faction="republic", owner_id=2))
    api_db.commit()

    response = api_client.get("/api/characters", headers=auth_headers(1))

    assert response.status_code == 200
    assert response.json()["total"] == 1


def test_character_list_supports_relationship_and_mine_filters(api_client: TestClient, api_db: Session) -> None:
    tank = api_db.scalar(select(Role).where(Role.name == "Tank"))
    dps = api_db.scalar(select(Role).where(Role.name == "DPS"))
    owned_character = Character(name="Tank Character", faction="republic", owner_id=2, roles=[tank])
    other_character = Character(name="DPS Character", faction="empire", owner_id=3, roles=[dps])
    api_db.add_all([owned_character, other_character])
    api_db.commit()

    role_response = api_client.get(
        f'/api/characters?filter={{"role_ids":[{tank.id}]}}',
        headers=auth_headers(1),
    )
    mine_response = api_client.get('/api/characters?filter={"mine":true}', headers=auth_headers(2))

    assert role_response.status_code == 200
    assert [record["name"] for record in role_response.json()["data"]] == ["Tank Character"]
    assert mine_response.status_code == 200
    assert [record["name"] for record in mine_response.json()["data"]] == ["Tank Character"]


def test_user_owned_constraints_return_bad_request(api_client: TestClient) -> None:
    response = api_client.post(
        "/api/items",
        json={
            "name": "Bound Shared Item",
            "bound": True,
            "cargo_hold": "cargo_hold_shared",
        },
        headers=auth_headers(2),
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Bound items must be stored in personal cargo hold."


def test_user_cannot_attach_record_to_another_users_character(api_client: TestClient, api_db: Session) -> None:
    character = Character(name="Other Character", faction="empire", owner_id=3)
    api_db.add(character)
    api_db.commit()

    response = api_client.post(
        "/api/items",
        json={"name": "Stolen Link", "character_ids": [character.id]},
        headers=auth_headers(2),
    )

    assert response.status_code == 403


def test_loadout_and_item_lists_support_character_and_mine_filters(
    api_client: TestClient,
    api_db: Session,
) -> None:
    owned_character = Character(name="Owned Character", faction="republic", owner_id=2)
    other_character = Character(name="Other Character", faction="empire", owner_id=3)
    loadout = Loadout(name="Owned Loadout", loadout_type="pve", owner_id=2, characters=[owned_character])
    item = Item(name="Owned Item", owner_id=2, characters=[owned_character])
    other_item = Item(name="Other Item", owner_id=3, characters=[other_character])
    api_db.add_all([owned_character, other_character, loadout, item, other_item])
    api_db.commit()

    loadout_response = api_client.get(
        f'/api/loadouts?filter={{"character_ids":[{owned_character.id}]}}',
        headers=auth_headers(2),
    )
    item_response = api_client.get(
        f'/api/items?filter={{"character_ids":[{owned_character.id}]}}',
        headers=auth_headers(2),
    )
    mine_response = api_client.get('/api/items?filter={"mine":true}', headers=auth_headers(2))

    assert loadout_response.status_code == 200
    assert [record["name"] for record in loadout_response.json()["data"]] == ["Owned Loadout"]
    assert item_response.status_code == 200
    assert [record["name"] for record in item_response.json()["data"]] == ["Owned Item"]
    assert mine_response.status_code == 200
    assert [record["name"] for record in mine_response.json()["data"]] == ["Owned Item"]
