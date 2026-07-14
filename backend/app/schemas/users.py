from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UserRead(BaseModel):
    id: int
    username: str
    is_active: bool
    is_swtor_admin: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserListResponse(BaseModel):
    data: list[UserRead]
    total: int


class UserCreate(BaseModel):
    username: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=8, max_length=255)
    is_active: bool = True
    is_swtor_admin: bool = False


class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=1, max_length=255)
    password: str | None = Field(default=None, min_length=8, max_length=255)
    is_active: bool | None = None
    is_swtor_admin: bool | None = None
