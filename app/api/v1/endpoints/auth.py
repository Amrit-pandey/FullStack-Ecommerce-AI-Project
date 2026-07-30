import secrets
from typing import Annotated

from fastapi import APIRouter, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.redis import check_and_set_cooldown, set_otp, verify_and_delete_otp
from app.db.database import get_db
from app.schemas.auth import OTPRequest
from app.services.email_service import send_otp_email

router = APIRouter()

@router.post("/request_otp", status_code=status.HTTP_200_OK)
async def request_otp(payload: OTPRequest):
    email = payload.email.lower()

    allowed = await check_and_set_cooldown(email, seconds=60)
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Please wait 60 seconds before requesting another OTP."
        )

    generate_otp = f"{secrets.randbelow(1000000):06d}"

    await set_otp(email, code=generate_otp)

    await send_otp_email(email, otp_code=generate_otp)

    return {"message": "OTP sent successfully to your email"}

