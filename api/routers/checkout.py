import uuid

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from yookassa import Payment

from api.deps import SessionDep, UserDep
from api.schemas import CreateCheckout
from api.services.addresses import calculate_delivery_price
from config import settings
from db.crud import (
    add_order_items,
    calculate_total_price,
    create_order,
    get_item_price,
    get_items,
    update_order_payment_id,
)

router = APIRouter()


class CheckoutResponse(BaseModel):
    payment_url: str


@router.post("", response_model=CheckoutResponse)
async def get_checkout(checkout_data: CreateCheckout, db: SessionDep, user: UserDep):
    delivery_price = await calculate_delivery_price(checkout_data.address)
    if delivery_price is None and not checkout_data.other_delivery_method:
        raise HTTPException(400, "invalid address")
    total_price = calculate_total_price(db, checkout_data.items) + (delivery_price or 0)

    order = create_order(
        db,
        user_id=user.id,
        total_price=total_price,
        payment_id="payment.id",
        email=checkout_data.email,
        address=checkout_data.address,
        address_details=checkout_data.address_details,
        other_delivery_method=checkout_data.other_delivery_method,
        delivery_price=delivery_price,
        fio=checkout_data.fio,
        phone=checkout_data.phone,
    )
    username = user.username
    quantities = {item.id: item.quantity for item in checkout_data.items}
    prices: dict[int, int] = {}
    for item in checkout_data.items:
        size = get_item_price(db, item.id, item.size)
        if size is None:
            raise HTTPException(400, "invalid item size")
        prices[item.id] = size.price

    payment = Payment.create(
        {
            "amount": {"value": f"{total_price}.00", "currency": "RUB"},
            "confirmation": {
                "type": "redirect",
                "return_url": f"{settings.FRONTEND_URL}/order/{order.id}?redirected=true",  # noqa: E501
            },
            "capture": True,
            "description": f"Заказ {'@' + username if username else ''} {order.created_at_str}",  # noqa: E501
            "receipt": {
                "customer": {"email": checkout_data.email},
                "items": ([
                    {
                        "payment_subject": "service",
                        "description": "Доставка",
                        "amount": {
                            "value": f"{delivery_price}.00",
                            "currency": "RUB",
                        },
                        "vat_code": 9,
                        "quantity": 1,
                        "measure": "piece",
                    }
                ]
                if delivery_price
                else [])
                + [
                    {
                        "description": item.name,
                        "payment_subject": "commodity",
                        "amount": {
                            "value": f"{prices[item.id]}.00",
                            "currency": "RUB",
                        },
                        "vat_code": 9,
                        "quantity": quantities[item.id],
                        "measure": "piece",
                    }
                    for item in get_items(db, [item.id for item in checkout_data.items])
                ],
            },
        },
        uuid.uuid4(),
    )
    update_order_payment_id(db, order, payment.id)  # type: ignore
    add_order_items(db, order_id=order.id, items=checkout_data.items, prices=prices)

    # print(user.username, user.tg_id, user.first_name)

    # return

    if payment.confirmation is None:
        raise Exception
    return {"payment_url": payment.confirmation.confirmation_url}
