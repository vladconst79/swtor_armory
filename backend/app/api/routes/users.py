import json
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import asc, desc, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.dependencies import require_swtor_admin
from app.core.security import get_password_hash
from app.db.session import get_db
from app.models.user import User
from app.schemas.users import UserCreate, UserListResponse, UserRead, UserUpdate

router = APIRouter(prefix="/users")


def _parse_filter(raw_filter: str | None) -> dict[str, Any]:
    if raw_filter is None:
        return {}
    try:
        parsed = json.loads(raw_filter)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Filter must be valid JSON.") from exc
    if not isinstance(parsed, dict):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Filter must be a JSON object.")
    return parsed


def _apply_filters(query, filters: dict[str, Any]):
    for field, value in filters.items():
        if value is None or value == "":
            continue
        if field == "q":
            query = query.where(User.username.ilike(f"%{value}%"))
        elif field == "id":
            values = value if isinstance(value, list) else [value]
            query = query.where(User.id.in_(values))
        elif field == "username":
            query = query.where(User.username.ilike(f"%{value}%"))
        elif field == "is_active":
            query = query.where(User.is_active == bool(value))
        elif field == "is_swtor_admin":
            query = query.where(User.is_swtor_admin == bool(value))
    return query


def _sort_column(sort: str):
    return {
        "id": User.id,
        "username": User.username,
        "is_active": User.is_active,
        "is_swtor_admin": User.is_swtor_admin,
        "created_at": User.created_at,
        "updated_at": User.updated_at,
    }.get(sort, User.id)


def _commit_user(db: Session, user: User) -> User:
    db.add(user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists.") from exc
    db.refresh(user)
    return user


@router.get("", response_model=UserListResponse)
def list_users(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=25, ge=1, le=100),
    sort: str = "id",
    order: str = "asc",
    filter: str | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(require_swtor_admin),
) -> UserListResponse:
    filters = _parse_filter(filter)
    base_query = _apply_filters(select(User), filters)
    total = db.scalar(select(func.count()).select_from(base_query.subquery())) or 0

    sort_expression = _sort_column(sort)
    sort_expression = desc(sort_expression) if order.lower() == "desc" else asc(sort_expression)
    users = db.scalars(base_query.order_by(sort_expression).offset((page - 1) * per_page).limit(per_page)).all()
    return UserListResponse(data=[UserRead.model_validate(user) for user in users], total=total)


@router.get("/{user_id}", response_model=UserRead)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_swtor_admin),
) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    return user


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_swtor_admin),
) -> User:
    user = User(
        username=payload.username,
        hashed_password=get_password_hash(payload.password),
        is_active=payload.is_active,
        is_swtor_admin=payload.is_swtor_admin,
    )
    return _commit_user(db, user)


@router.patch("/{user_id}", response_model=UserRead)
def update_user(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_swtor_admin),
) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    if payload.username is not None:
        user.username = payload.username
    if payload.password:
        user.hashed_password = get_password_hash(payload.password)
    if payload.is_active is not None:
        if user.id == current_user.id and not payload.is_active:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You cannot deactivate your own user.")
        user.is_active = payload.is_active
    if payload.is_swtor_admin is not None:
        if user.id == current_user.id and not payload.is_swtor_admin:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You cannot remove your own admin privileges.")
        user.is_swtor_admin = payload.is_swtor_admin

    return _commit_user(db, user)
