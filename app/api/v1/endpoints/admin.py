from typing import Annotated

from fastapi import APIRouter

from app.models.user import User

router = APIRouter()

@router.get("/test")
async def test_admin():
    return {
        "message": "Admin access granted",
    }