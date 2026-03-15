from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

from app.models.enums import UserRole


class UserSummary(BaseModel):
    id: int
    username: str
    role: UserRole

    model_config = ConfigDict(from_attributes=True)


class UserRead(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: UserRole
    bio: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
