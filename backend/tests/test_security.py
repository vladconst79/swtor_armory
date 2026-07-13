from datetime import timedelta

import jwt

from app.core.security import (
    create_access_token,
    decode_access_token,
    get_password_hash,
    verify_password,
)


def test_password_hash_verifies_original_password() -> None:
    hashed_password = get_password_hash("correct horse battery staple")

    assert hashed_password != "correct horse battery staple"
    assert verify_password("correct horse battery staple", hashed_password)
    assert not verify_password("wrong password", hashed_password)


def test_access_token_round_trip() -> None:
    token = create_access_token(
        subject="user-1",
        expires_delta=timedelta(minutes=5),
        additional_claims={"is_swtor_admin": True},
    )

    payload = decode_access_token(token)

    assert payload["sub"] == "user-1"
    assert payload["is_swtor_admin"] is True
    assert "exp" in payload


def test_expired_access_token_is_rejected() -> None:
    token = create_access_token(subject="user-1", expires_delta=timedelta(seconds=-1))

    try:
        decode_access_token(token)
    except jwt.ExpiredSignatureError:
        return

    raise AssertionError("expired token should be rejected")
