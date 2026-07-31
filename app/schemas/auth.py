from pydantic import BaseModel, EmailStr, Field

from app.schemas.user import UserPublic


class OTPRequest(BaseModel):
    email: EmailStr = Field(..., max_length=255, description="User email address")


class OTPVerify(BaseModel):
    email: EmailStr
    otp: str = Field(
        ..., min_length=6, max_length=6, pattern=r"^\d{6}$", examples=["123456"]
    )


class LoginResponse(BaseModel):
    is_new_user: bool
    user: UserPublic
