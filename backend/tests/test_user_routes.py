from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.security import create_access_token, get_password_hash, verify_password
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.user import User


@pytest.fixture
def user_db() -> Generator[Session, None, None]:
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
            ]
        )
        db.commit()
        yield db
    finally:
        db.close()


@pytest.fixture
def user_client(user_db: Session) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        yield user_db

    app.dependency_overrides[get_db] = override_get_db
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


def auth_headers(user_id: int) -> dict[str, str]:
    token = create_access_token(subject=str(user_id))
    return {"Authorization": f"Bearer {token}"}


def test_admin_can_list_users_without_hashes(user_client: TestClient) -> None:
    response = user_client.get("/api/users", headers=auth_headers(1))

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert body["data"][0]["username"] == "admin"
    assert "hashed_password" not in body["data"][0]


def test_normal_user_cannot_manage_users(user_client: TestClient) -> None:
    response = user_client.get("/api/users", headers=auth_headers(2))

    assert response.status_code == 403


def test_admin_can_create_user_with_hashed_password(user_client: TestClient, user_db: Session) -> None:
    response = user_client.post(
        "/api/users",
        headers=auth_headers(1),
        json={
            "username": "new-user",
            "password": "new-password",
            "is_active": True,
            "is_swtor_admin": False,
        },
    )

    assert response.status_code == 201
    user = user_db.get(User, response.json()["id"])
    assert user is not None
    assert user.hashed_password != "new-password"
    assert verify_password("new-password", user.hashed_password)


def test_admin_can_reset_user_password(user_client: TestClient, user_db: Session) -> None:
    response = user_client.patch(
        "/api/users/2",
        headers=auth_headers(1),
        json={"password": "changed-password"},
    )

    assert response.status_code == 200
    user = user_db.get(User, 2)
    assert user is not None
    assert verify_password("changed-password", user.hashed_password)


def test_admin_cannot_deactivate_self(user_client: TestClient) -> None:
    response = user_client.patch(
        "/api/users/1",
        headers=auth_headers(1),
        json={"is_active": False},
    )

    assert response.status_code == 400


def test_admin_cannot_remove_own_admin_role(user_client: TestClient) -> None:
    response = user_client.patch(
        "/api/users/1",
        headers=auth_headers(1),
        json={"is_swtor_admin": False},
    )

    assert response.status_code == 400


def test_duplicate_username_is_rejected(user_client: TestClient) -> None:
    response = user_client.post(
        "/api/users",
        headers=auth_headers(1),
        json={"username": "normal", "password": "new-password"},
    )

    assert response.status_code == 400
