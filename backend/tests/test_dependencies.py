import pytest
from fastapi import HTTPException

from app.api.dependencies import require_swtor_admin
from app.models.user import User


def make_user(is_swtor_admin: bool) -> User:
    return User(
        id=1,
        username="vlad",
        hashed_password="hashed",
        is_active=True,
        is_swtor_admin=is_swtor_admin,
    )


def test_require_swtor_admin_accepts_admin_user() -> None:
    user = make_user(is_swtor_admin=True)

    assert require_swtor_admin(user) is user


def test_require_swtor_admin_rejects_normal_user() -> None:
    with pytest.raises(HTTPException) as exc_info:
        require_swtor_admin(make_user(is_swtor_admin=False))

    assert exc_info.value.status_code == 403
