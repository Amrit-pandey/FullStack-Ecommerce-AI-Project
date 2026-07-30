import secrets
from datetime import UTC, datetime, timedelta
from typing import Annotated

import models.user
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.redis import check_and_set_cooldown, set_otp, verify_and_delete_otp
from app.core.security import create_access_token
from app.db.database import get_db
from app.schemas.auth import OTPRequest, OTPVerify, TokenResponse
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

@router.post("/verify_otp", status_code=status.HTTP_200_OK)
async def verify_otp(payload: OTPVerify, db: Annotated[AsyncSession, Depends(get_db)]):
    email = payload.email.lower()
    otp = payload.otp

    is_valid = await verify_and_delete_otp(email=email, input_code=otp)

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid and expire OTP"
        )

    result = await db.execute(
        select(models.user.User).where(models.user.User.email == email)
    )
    user = result.scalars().first()

    is_new_user = False

    if not user:
        user = models.user.User(email=email, is_active= True)
        db.add(user)
        user.last_login = datetime.now(UTC)
        await db.commit()
        await db.refresh(user)
        is_new_user= True

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account is inactive or suspended",
        )

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires ,
        is_new_user = is_new_user,
        user = user
    )
    return TokenResponse(access_token=access_token, token_type="bearer")