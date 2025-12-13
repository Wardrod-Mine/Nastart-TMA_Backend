from pydantic import BaseModel, EmailStr

from db.models import ProductCategory, ProductFlavour


class CartItem(BaseModel):
    quantity: int
    id: int
    size: str


class CreateCheckout(BaseModel):
    items: list[CartItem]
    address: str
    address_details: str
    other_delivery_method: str | None
    fio: str
    phone: str
    email: EmailStr


class ImageResponse(BaseModel):
    url: str


class ItemSizeResponse(BaseModel):
    size: str
    price: int


class ItemResponse(BaseModel):
    id: int
    name: str
    price: int | None = None
    category: ProductCategory | None = None
    flavour: ProductFlavour | None = None
    description: str
    images: list[ImageResponse]
    sizes: list[ItemSizeResponse]


class OrderItemResponse(BaseModel):
    id: int
    quantity: int
    item_id: int
    item_price: int
    item_size: str
    item: ItemResponse

    class Config:
        from_attributes = True


class OrderResponseBase(BaseModel):
    id: int
    order_details: str
    user_id: int
    total_price: int
    address: str
    address_details: str
    delivery_price: int | None
    payment_status: str
    created_at_str: str

    class Config:
        from_attributes = True


class OrderResponseItems(OrderResponseBase):
    items: list[OrderItemResponse]
