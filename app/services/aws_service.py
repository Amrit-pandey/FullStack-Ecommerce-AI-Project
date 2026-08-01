import uuid
from pathlib import Path

import boto3
from botocore.exceptions import ClientError
from fastapi import HTTPException, UploadFile, status
from starlette.concurrency import run_in_threadpool

from app.core.config import settings
from app.utils.logger import logger


def _create_s3_client():
    return boto3.client(
        "s3",
        region_name=settings.aws_region,
        aws_access_key_id=settings.aws_access_key_id.get_secret_value(),
        aws_secret_access_key=settings.aws_secret_access_key.get_secret_value(),
    )


s3_client = _create_s3_client()
bucket_name = settings.aws_s3_bucket_name


async def upload_to_s3(file: UploadFile, user_id: int) -> str:
    try:
        filename = file.filename
        if not filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="filename is missing"
            )
        # Generate unique filename
        # Extract and normalize the suffix (makes it ".png")
        extension = Path(filename).suffix.lower()
        # Generate the random string like "c2b0d5b8-f5aa-49f7-a52d-3f0cf2fef8c6.png" to avoid path collision in s3
        filename = f"{uuid.uuid4()}{extension}"
        logger.info("s3 filename: %s", filename)

        ALLOWED_EXTENTIONS = {".jpg", ".jpeg", ".png", ".webp"}
        if extension not in ALLOWED_EXTENTIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only JPG, JPEG, PNG and WEBP images are allowed."
            )

        # s3_object_key, it will save in db like users/1/c2b0d5b8-f5aa-49f7-a52d-3f0cf2fef8c6.png
        object_key = f"users/{user_id}/{filename}"
        logger.info("s3 object_key: %s", object_key)

        CONTENT_TYPE_MAPPING = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".webp": "image/webp"
        }

        content_type = CONTENT_TYPE_MAPPING.get(extension, "binary/octet-stream")

        # upload to s3, because boto3 runs synchronously and block the async event loop, that's why use run_in_threaspool for async endpoints
        await run_in_threadpool(
            s3_client.upload_fileobj,
            file.file,
            bucket_name,
            object_key,
            ExtraArgs={
                "ContentType": content_type
            },
        )
        return object_key
    except ClientError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload image",
        )

# This function generate full s3 url from backend because this url is saved as path like users/1/hdsbchd.png that's not valid for frontend to use
def generate_signed_url(object_key: str | None) -> str | None:
    try:
        if not object_key:
            return None
        
        return s3_client.generate_presigned_url(
            ClientMethod="get_object",
            Params={
                "Bucket": bucket_name,
                "Key": object_key,
            },
            ExpiresIn=3600,
        )

    except ClientError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate image URL",
        )