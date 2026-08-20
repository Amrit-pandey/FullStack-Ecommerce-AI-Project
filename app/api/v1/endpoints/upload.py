from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser
from app.db.database import get_db
from app.services.aws_service import upload_to_s3

router = APIRouter()


@router.post("/profile-image", status_code=status.HTTP_200_OK)
async def upload_profile_image(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    file: UploadFile = File(...),
):

    object_key = await upload_to_s3(file=file, object_prefix=f"users/{current_user.id}")

    current_user.image_url = object_key

    await db.commit()
    await db.refresh(current_user)
    return {"message": "Profile image uploaded successfully"}


@router.post("/product-image", status_code=status.HTTP_200_OK)
async def upload_product_image(
    file: UploadFile = File(...)
):
    object_key = await upload_to_s3(
        file=file,
        object_prefix="products"
    )

    return {
        "message": "Product image uploaded successfully",
        "image_url": object_key
    }