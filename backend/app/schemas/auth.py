from pydantic import BaseModel, ConfigDict


class LoginRequest(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str
    exp: int
    is_swtor_admin: bool = False


class CurrentUser(BaseModel):
    id: int
    username: str
    is_active: bool
    is_swtor_admin: bool

    model_config = ConfigDict(from_attributes=True)
