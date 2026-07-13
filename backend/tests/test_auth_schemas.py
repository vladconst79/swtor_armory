from app.models.user import User
from app.schemas.auth import CurrentUser, LoginRequest, Token


def test_login_request_schema() -> None:
    login = LoginRequest(username="vlad", password="secret")

    assert login.username == "vlad"
    assert login.password == "secret"


def test_token_defaults_to_bearer_type() -> None:
    token = Token(access_token="abc123")

    assert token.access_token == "abc123"
    assert token.token_type == "bearer"


def test_current_user_schema_can_validate_user_model() -> None:
    user = User(
        id=1,
        username="vlad",
        hashed_password="hashed",
        is_active=True,
        is_swtor_admin=False,
    )

    current_user = CurrentUser.model_validate(user)

    assert current_user.model_dump() == {
        "id": 1,
        "username": "vlad",
        "is_active": True,
        "is_swtor_admin": False,
    }
