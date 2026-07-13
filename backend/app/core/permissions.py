from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.sql import Select

from app.models.user import User


def assert_owner_or_admin(record: Any, current_user: User) -> None:
    owner_id = getattr(record, "owner_id", None)
    if current_user.is_swtor_admin or owner_id == current_user.id:
        return

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Not enough permissions for this record",
    )


def apply_owner_filter(query: Select[Any], model: type[Any], current_user: User) -> Select[Any]:
    if current_user.is_swtor_admin:
        return query
    return query.where(model.owner_id == current_user.id)


def require_reference_write_permission(current_user: User) -> None:
    if current_user.is_swtor_admin:
        return

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="SWTOR admin privileges required",
    )
