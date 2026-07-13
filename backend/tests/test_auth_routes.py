from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.security import create_access_token, decode_access_token, get_password_hash
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.user import User


@pytest.fixture
def auth_db() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        db.add(
            User(
                username="vlad",
                hashed_password=get_password_hash("secret"),
                is_active=True,
                is_swtor_admin=True,
            )
        )
        db.add(
            User(
                username="inactive",
                hashed_password=get_password_hash("secret"),
                is_active=False,
                is_swtor_admin=False,
            )
        )
        db.add(
            User(
                username="normal",
                hashed_password=get_password_hash("secret"),
                is_active=True,
                is_swtor_admin=False,
            )
        )
        db.commit()
        yield db
    finally:
        db.close()


@pytest.fixture
def auth_client(auth_db: Session) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        yield auth_db

    app.dependency_overrides[get_db] = override_get_db
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


def test_login_returns_bearer_token(auth_client: TestClient) -> None:
    response = auth_client.post(
        "/api/auth/login",
        json={"username": "vlad", "password": "secret"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"

    payload = decode_access_token(body["access_token"])
    assert payload["sub"] == "1"
    assert payload["is_swtor_admin"] is True


def test_login_rejects_invalid_password(auth_client: TestClient) -> None:
    response = auth_client.post(
        "/api/auth/login",
        json={"username": "vlad", "password": "wrong"},
    )

    assert response.status_code == 401


def test_login_rejects_inactive_user(auth_client: TestClient) -> None:
    response = auth_client.post(
        "/api/auth/login",
        json={"username": "inactive", "password": "secret"},
    )

    assert response.status_code == 401


def test_me_returns_current_user(auth_client: TestClient) -> None:
    login_response = auth_client.post(
        "/api/auth/login",
        json={"username": "normal", "password": "secret"},
    )
    access_token = login_response.json()["access_token"]

    response = auth_client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": 3,
        "username": "normal",
        "is_active": True,
        "is_swtor_admin": False,
    }


def test_me_requires_token(auth_client: TestClient) -> None:
    response = auth_client.get("/api/auth/me")

    assert response.status_code == 401


def test_me_rejects_inactive_user(auth_client: TestClient) -> None:
    access_token = create_access_token(subject="2")

    response = auth_client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 403
