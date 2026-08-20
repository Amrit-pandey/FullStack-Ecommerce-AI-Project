from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.products import Product
from app.models.user import User
from app.schemas.products import (
    AdminProductCreateRequest,
    AdminProductCreateResponse,
    AdminProductsResponse,
)
from app.schemas.user import (
    UserActionStatusRequest,
    UserActionStatusResponse,
    UserResponse,
)
from app.utils.logger import logger

router = APIRouter()

@router.get("/test")
async def test_admin():
    return {
        "message": "Admin access granted",
    }


@router.get("/users", response_model=UserResponse)
async def get_users(
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = 1,
    limit: int = 10,
    search: str | None = None,
):
    offset = (page - 1) * limit
    query = select(User)

    if search:
        query = query.where(
            or_(
                User.email.ilike(f"%{search}%"),
                User.full_name.ilike(f"%{search}%")
            )
        )

    count_query = select(func.count()).select_from(query.subquery())
    count_result = await db.execute(count_query)
    total_count = count_result.scalar_one()

    query = query.offset(offset).limit(limit).order_by(User.created_at.desc())
    result = await db.execute(query)
    users = result.scalars().all()

    return {"users": users, "page": page, "limit": limit, "total_count": total_count}


@router.post('/user/deactivate', response_model= UserActionStatusResponse)
async def deactivate_user(request: UserActionStatusRequest, db: Annotated[AsyncSession, Depends(get_db)]):
    user_id = request.id

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    print(user, "userId")

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="user not found"
        )

    user.is_active = False

    response = UserActionStatusResponse(
        message = "User account successfully deactivated",
        user = user
    )
    return response


@router.post('/user/activate', response_model= UserActionStatusResponse)
async def activate_user(request: UserActionStatusRequest, db: Annotated[AsyncSession, Depends(get_db)]):
    user_id = request.id

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="user not found"
        )

    user.is_active = True

    response = UserActionStatusResponse(
        message = "User account successfully activated",
        user = user
    )

    return response


@router.post("/add_product", response_model= AdminProductCreateResponse)
async def create_product(payload: AdminProductCreateRequest, db: Annotated[AsyncSession, Depends(get_db)]):
    try:
        product = Product(
            title= payload.title,
            description= payload.description,
            image_url= payload.image_url,
            price= payload.price,
            in_stock= payload.in_stock,
            stock_quantity= payload.stock_quantity
        )
        db.add(product)
        response = AdminProductCreateResponse(
            message= "Product created successfully",
            product= product
        )
        return response
    except Exception:
        logger.exception("Failed to create product..")
        raise


@router.get("/products", response_model= AdminProductsResponse)
async def get_products(db: Annotated[AsyncSession, Depends(get_db)], search: str | None = None):

    query = select(Product)

    if search:
        query = query.where(Product.title.ilike(f"%{search}%"))

    result = await db.execute(query)
    products = result.scalars().all()

    response = AdminProductsResponse(
        message= "Products fetched successfully",
        products= products
    )

    return response