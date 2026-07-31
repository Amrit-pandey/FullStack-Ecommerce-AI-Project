from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser
from app.db.database import get_db
from app.schemas.user import OnboardingRequest, UserPublic

router = APIRouter()

@router.get("/me", response_model=UserPublic, status_code=status.HTTP_200_OK)
async def get_current_user(current_user: CurrentUser):
    return current_user

@router.post("/onboarding", response_model=OnboardingRequest, status_code=status.HTTP_201_CREATED)
async def onboarding(payload: OnboardingRequest, current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    full_name = payload.full_name.strip()
    image_file = payload.image_file

    if current_user.full_name is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Onboarding already completed"
        )

    # image upload logic if user uploads the image then run logic otherwise defualt to None A/c to schema
    #  After complete onboarding we'll get the first charecter from full_name and display in frontend as avatar

    current_user.full_name = full_name
    current_user.image_file = image_file

    await db.commit()
    await db.refresh(current_user)

    return {"message": "Onboarding completed successfully"}