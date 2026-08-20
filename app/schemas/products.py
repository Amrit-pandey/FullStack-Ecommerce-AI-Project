from pydantic import BaseModel, ConfigDict, Field


class AdminProductCreateRequest(BaseModel):
    title: str = Field(max_length=100, min_length=1)
    description: str = Field(max_length=250, min_length=1)
    image_url: str | None = None
    price: int
    in_stock: bool
    stock_quantity: int


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    image_url: str | None
    price: int
    in_stock: bool
    stock_quantity: int


class AdminProductCreateResponse(BaseModel):
    message: str
    product: ProductResponse


class AdminProductsResponse(BaseModel):
    message: str
    product: list[ProductResponse]