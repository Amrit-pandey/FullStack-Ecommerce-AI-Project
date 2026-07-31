from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.user import UserRole


class OnboardingRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    image_url: str | None = None


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str | None
    email: EmailStr
    role: UserRole
    image_url: str | None
    is_active: bool
    created_at: datetime