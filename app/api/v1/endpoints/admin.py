from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.user import User

router = APIRouter()

@router.get("/test")
async def test_admin():
    return {
        "message": "Admin access granted",
    }

@router.get("/users")
async def get_users(db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(User))
    users = result.scalars().all()

    if not users:
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail="No users yet"
        )

    return users