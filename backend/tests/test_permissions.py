from dataclasses import dataclass

import pytest
from fastapi import HTTPException
from sqlalchemy import Column, Integer, MetaData, Table, select

from app.core.permissions import (
    apply_owner_filter,
    assert_owner_or_admin,
    require_reference_write_permission,
)
from app.models.user import User


@dataclass
class OwnedRecord:
    owner_id: int


def make_user(user_id: int, is_swtor_admin: bool = False) -> User:
    return User(
        id=user_id,
        username=f"user-{user_id}",
        hashed_password="hashed",
        is_active=True,
        is_swtor_admin=is_swtor_admin,
    )


def test_assert_owner_or_admin_allows_owner() -> None:
    assert_owner_or_admin(OwnedRecord(owner_id=1), make_user(1))


def test_assert_owner_or_admin_allows_admin() -> None:
    assert_owner_or_admin(OwnedRecord(owner_id=2), make_user(1, is_swtor_admin=True))


def test_assert_owner_or_admin_rejects_other_user() -> None:
    with pytest.raises(HTTPException) as exc_info:
        assert_owner_or_admin(OwnedRecord(owner_id=2), make_user(1))

    assert exc_info.value.status_code == 403


def test_apply_owner_filter_limits_normal_users() -> None:
    table = Table("owned_records", MetaData(), Column("owner_id", Integer))

    class OwnedModel:
        owner_id = table.c.owner_id

    query = apply_owner_filter(select(table), OwnedModel, make_user(7))

    compiled = query.compile(compile_kwargs={"literal_binds": True})
    assert "owned_records.owner_id = 7" in str(compiled)


def test_apply_owner_filter_does_not_limit_admins() -> None:
    table = Table("owned_records", MetaData(), Column("owner_id", Integer))

    class OwnedModel:
        owner_id = table.c.owner_id

    query = apply_owner_filter(select(table), OwnedModel, make_user(7, is_swtor_admin=True))

    assert "WHERE" not in str(query.compile())


def test_require_reference_write_permission_allows_admin() -> None:
    require_reference_write_permission(make_user(1, is_swtor_admin=True))


def test_require_reference_write_permission_rejects_normal_user() -> None:
    with pytest.raises(HTTPException) as exc_info:
        require_reference_write_permission(make_user(1))

    assert exc_info.value.status_code == 403
