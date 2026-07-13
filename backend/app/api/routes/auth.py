from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user
from app.core.security import create_access_token
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import CurrentUser, LoginRequest, Token
from app.services.auth import authenticate_user

router = APIRouter(prefix="/auth")


@router.post("/login", response_model=Token)
def login(login_request: LoginRequest, db: Session = Depends(get_db)) -> Token:
    user = authenticate_user(db, login_request.username, login_request.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        subject=str(user.id),
        additional_claims={"is_swtor_admin": user.is_swtor_admin},
    )
    return Token(access_token=access_token)


@router.get("/me", response_model=CurrentUser)
def get_me(current_user: User = Depends(get_current_active_user)) -> User:
    return current_user
