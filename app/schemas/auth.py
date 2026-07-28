from datetime import datetime

from models.user import UserRole
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class OTPRequest(BaseModel):
    username: str | None = Field(None, min_length=3, max_length=50, description="Required for first-time user creation")
    email: EmailStr = Field(..., max_length=255, description="User email address")

class OTPVerify(BaseModel):
    email: EmailStr = Field(..., max_length=250)
    otp: str = Field(min_length=6, max_length=6, pattern=r"^\d{6}$", examples=["123456"])

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    role: UserRole
    is_active: bool
    created_at: datetime

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse