import enum
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db import Base


class PaymentStatus(enum.Enum):
    PENDING = "pending"
    WAITING_FOR_CAPTURE = "waiting_for_capture"
    SUCCEEDED = "succeeded"
    CANCELED = "canceled"


class ProductCategory(enum.Enum):
    PUPPIES = "Щенки"
    CATS_1 = "Взрослые кошки (1+ лет)"
    DOGS_1_6 = "Взрослые собаки (1-6 лет)"
    DOGS_7 = "Взрослые собаки (7+ лет)"
    ZAPECHENIY = "Запеченный корм для собак всех возрастов"


class ProductFlavour(enum.Enum):
    BARANINA = "Баранина"
    INDEYKA = "Индейка"
    OLENINA = "Оленина"
    YTKA = "Утка"


class DeliveryMethod(enum.Enum):
    CDEK = "СДЭК"
    DELOVIE_LINII = "Деловые линии"


class ItemSize(Base):
    __tablename__ = "item_sizes"

    id: Mapped[int] = mapped_column(primary_key=True)
    size: Mapped[str] = mapped_column(String)
    price: Mapped[int] = mapped_column(Integer)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"))
    # active: Mapped[bool] = mapped_column(default=True)

    item: Mapped["Item"] = relationship("Item", back_populates="sizes")


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)
    active: Mapped[bool] = mapped_column(default=True)
    flavour: Mapped[ProductFlavour | None]
    category: Mapped[ProductCategory | None]

    images: Mapped[list["Image"]] = relationship(
        "Image", back_populates="item", cascade="all, delete-orphan"
    )
    sizes: Mapped[list["ItemSize"]] = relationship(
        "ItemSize", back_populates="item", cascade="all, delete-orphan"
    )


class Image(Base):
    __tablename__ = "images"

    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(String)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"))

    item: Mapped[Item] = relationship("Item", back_populates="images")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger)
    first_name: Mapped[str] = mapped_column(String)
    username: Mapped[str | None] = mapped_column(String, nullable=True)

    orders: Mapped[list["Order"]] = relationship(
        "Order", back_populates="user", cascade="all, delete-orphan"
    )


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_details: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    total_price: Mapped[int] = mapped_column(Integer)

    user: Mapped[User] = relationship("User", back_populates="orders")
    items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem", back_populates="order", cascade="all, delete-orphan"
    )
    other_delivery_method: Mapped[DeliveryMethod | None]
    fio: Mapped[str]
    phone: Mapped[str]
    address: Mapped[str]
    address_details: Mapped[str]
    delivery_price: Mapped[int | None]
    payment_id: Mapped[str]
    payment_status: Mapped[PaymentStatus]
    receipt_email: Mapped[str]

    @property
    def created_at_str(self):
        return self.created_at.strftime("%d.%m.%Y %H:%M")


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    quantity: Mapped[int] = mapped_column(Integer)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"))
    item_size: Mapped[str]
    item_price: Mapped[int]
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))

    item: Mapped[Item] = relationship("Item")
    order: Mapped[Order] = relationship("Order", back_populates="items")
