# this script is useful when configured system/user/resource in a required state.
# for example: when we want to convert a secific user to admin.

import asyncio

from sqlalchemy import select

from app.core.config import settings
from app.db.database import AsyncSessionLocal
from app.models.user import User, UserRole
from app.utils.logger import logger


async def provision_script():
    admin_email = settings.admin_email
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.email == admin_email))
        user = result.scalars().first()

        if not user:
            raise ValueError("User not found")

        user.role = UserRole.ADMIN

        await session.commit()
        await session.refresh(user)

    return { "message": f"Admin provisioned successfully for {admin_email}"}

if __name__ == "__main__":
    output = asyncio.run(provision_script())
    logger.info(output)