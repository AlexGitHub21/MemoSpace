import datetime
import uuid

from pydantic import BaseModel, EmailStr


class GetUserByID(BaseModel):
    id: int | str


class GetUserByEmail(BaseModel):
    email: EmailStr


class AuthUser(GetUserByEmail):
    password: str


class CreateUser(GetUserByEmail):
    hashed_password: str


class UserReturnData(GetUserByID, GetUserByEmail):
    is_active: bool
    is_verified: bool
    is_superuser: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime


class GetUserWithIDAndEmail(GetUserByID, CreateUser):
    pass


class UserVerifySchema(GetUserByID, GetUserByEmail):
    session_id: uuid.UUID | str | None = None


