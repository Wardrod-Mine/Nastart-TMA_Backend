from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from api.schemas import CartItem
from db.models import (
    DeliveryMethod,
    Image,
    Item,
    ItemSize,
    Order,
    OrderItem,
    PaymentStatus,
    ProductCategory,
    ProductFlavour,
    User,
)


def create_product(
    db: Session,
    name: str,
    prices: list[tuple[str, int]],
    description: str,
    images_urls: list[str],
):
    item = Item(
        name=name,
        description=description,
        sizes=[ItemSize(size=size, price=price) for size, price in prices],
        images=[Image(url=url) for url in images_urls],
    )
    db.add(item)
    db.commit()


def delete_item(db: Session, item_id: int):
    item = db.execute(select(Item).where(Item.id == item_id)).scalar_one_or_none()
    if not item:
        raise ValueError(f"Item with id {item_id} not found.")
    item.active = False
    db.commit()


def update_item_name(db: Session, item_id: int, name: str):
    item = db.execute(select(Item).where(Item.id == item_id)).scalar_one_or_none()
    if not item:
        raise ValueError(f"Item with id {item_id} not found.")
    item.name = name
    db.commit()


def update_item_description(db: Session, item_id: int, description: str):
    item = db.execute(select(Item).where(Item.id == item_id)).scalar_one_or_none()
    if not item:
        raise ValueError(f"Item with id {item_id} not found.")
    item.description = description
    db.commit()


def update_item_sizes(db: Session, item_id: int, sizes: list[tuple[str, int]]):
    item = db.execute(select(Item).where(Item.id == item_id)).scalar_one_or_none()
    if not item:
        raise ValueError(f"Item with id {item_id} not found.")
    item.sizes.clear()
    for size, price in sizes:
        item.sizes.append(ItemSize(size=size, price=price))
    db.commit()


def update_item_images(db: Session, item_id: int, images_urls: list[str]):
    item = db.execute(select(Item).where(Item.id == item_id)).scalar_one_or_none()
    if not item:
        raise ValueError(f"Item with id {item_id} not found.")
    item.images = [Image(url=url) for url in images_urls]
    db.commit()


def update_item_flavour(db: Session, item_id: int, flavour: ProductFlavour):
    item = db.execute(select(Item).where(Item.id == item_id)).scalar_one_or_none()
    if not item:
        raise ValueError(f"Item with id {item_id} not found.")
    item.flavour = flavour
    db.commit()


def update_item_category(db: Session, item_id: int, category: ProductCategory):
    item = db.execute(select(Item).where(Item.id == item_id)).scalar_one_or_none()
    if not item:
        raise ValueError(f"Item with id {item_id} not found.")
    item.category = category
    db.commit()


def get_all_items(db: Session):
    return db.scalars(
        select(Item)
        .where(Item.active == True)
        .options(selectinload(Item.images), selectinload(Item.sizes))
        .order_by(Item.id.desc())
    ).all()


def get_item_by_id(db: Session, item_id: int) -> Item | None:
    return db.scalar(
        select(Item)
        .options(selectinload(Item.images), selectinload(Item.sizes))
        .where(Item.id == item_id)
    )


def get_prev_and_next_items(db: Session, item: Item) -> tuple[int | None, int | None]:
    prev_item = db.scalar(
        select(Item)
        .where(Item.id < item.id, Item.active == True)
        .order_by(Item.id.desc())
        .limit(1)
    )
    next_item = db.scalar(
        select(Item)
        .where(Item.id > item.id, Item.active == True)
        .order_by(Item.id.asc())
        .limit(1)
    )
    prev_item_id = None
    if prev_item:
        prev_item_id = prev_item.id
    next_item_id = None
    if next_item:
        next_item_id = next_item.id
    return prev_item_id, next_item_id


def get_first_item(db: Session) -> Item | None:
    return db.scalar(
        select(Item).where(Item.active == True).order_by(Item.id.asc()).limit(1)
    )


def get_or_create_user(
    db: Session, tg_id: int, first_name: str | None, username: str | None
) -> User:
    user = db.scalar(select(User).where(User.tg_id == tg_id))
    if user:
        return user
    user = User(tg_id=tg_id, first_name=first_name, username=username)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_item_price(db: Session, item_id: int, item_size: str) -> ItemSize | None:
    return db.scalar(
        select(ItemSize).where(ItemSize.size == item_size, ItemSize.item_id == item_id)
    )


def create_order(
    db: Session,
    user_id: int,
    total_price: int,
    email: str,
    payment_id: str,
    address: str,
    address_details: str,
    other_delivery_method: str | None,
    delivery_price: int | None,
    fio: str,
    phone: str,
) -> Order:
    order = Order(
        user_id=user_id,
        total_price=total_price,
        order_details="",
        created_at=datetime.now(),
        receipt_email=email,
        payment_id=payment_id,
        payment_status=PaymentStatus.PENDING,
        address=address,
        address_details=address_details,
        other_delivery_method=DeliveryMethod(other_delivery_method)
        if other_delivery_method
        else None,
        delivery_price=delivery_price,
        fio=fio,
        phone=phone,
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


def get_order_by_payment_id(db: Session, payment_id: str) -> Order | None:
    return db.scalar(select(Order).filter_by(payment_id=payment_id))


def update_order_status(db: Session, order: Order, status: PaymentStatus) -> None:
    order.payment_status = status
    db.commit()


def add_order_items(
    db: Session, order_id: int, items: list[CartItem], prices: dict[int, int]
) -> None:
    order_items = []
    for cart_item in items:
        item = db.execute(select(Item).filter_by(id=cart_item.id)).scalar_one_or_none()
        if not item:
            raise ValueError(f"Item with id {cart_item.id} not found.")
        order_items.append(
            OrderItem(
                order_id=order_id,
                item_id=item.id,
                quantity=cart_item.quantity,
                item_size=cart_item.size,
                item_price=prices[cart_item.id],
            )
        )
    db.add_all(order_items)
    db.commit()


def update_order_payment_id(db: Session, order: Order, payment_id: str):
    order.payment_id = payment_id
    db.add(order)
    db.commit()


def get_order(db: Session, order_id: int) -> Order | None:
    order = db.scalars(
        select(Order)
        .filter(Order.id == order_id)
        .options(
            selectinload(Order.items)
            .selectinload(OrderItem.item)
            .selectinload(Item.images)
        )
    ).one_or_none()
    return order


def get_user_orders(db: Session, user_id: int) -> list[Order]:
    orders = db.scalars(
        select(Order)
        .order_by(Order.created_at.desc())
        .filter(
            Order.user_id == user_id, Order.payment_status == PaymentStatus.SUCCEEDED
        )
        .options(selectinload(Order.items).selectinload(OrderItem.item))
    ).all()
    return list(orders)


def get_items(db: Session, item_ids: list[int]) -> list[Item]:
    stmt = select(Item).where(Item.id.in_(item_ids))
    return list(db.scalars(stmt).all())


def calculate_total_price(db: Session, items: list[CartItem]) -> int:
    total_price = 0
    for cart_item in items:
        item = db.execute(select(Item).filter_by(id=cart_item.id)).scalar_one_or_none()
        if not item:
            raise ValueError(f"Item with id {cart_item.id} not found.")
        for size in item.sizes:
            if size.size == cart_item.size:
                total_price += size.price * cart_item.quantity
                break
        else:
            raise ValueError(f"Size {cart_item.size} not found for item {item.id}.")
    return total_price


def get_user_by_tg_id(db: Session, tg_id: int) -> User | None:
    return db.execute(select(User).filter_by(tg_id=tg_id)).scalar_one_or_none()
