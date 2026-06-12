import datetime
import uuid
from pydantic import BaseModel, EmailStr, ConfigDict

class UpdateUserStatusSchema(BaseModel):
    is_superuser: bool


class GetUserByID(BaseModel):
    id: int | str


class GetUserByEmail(BaseModel):
    email: EmailStr


class UserReturnData(GetUserByID, GetUserByEmail):
    is_active: bool
    is_verified: bool
    is_superuser: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


class AdminVerifySchema(GetUserByID, GetUserByEmail):
    session_id: uuid.UUID | str | None = None
    is_superuser: bool


