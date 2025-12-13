from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from yookassa import Payment

from api.deps import SessionDep
from api.services.mail import send_email
from bot.init_bot import bot
from config import settings
from db.crud import get_order_by_payment_id, update_order_status
from db.models import PaymentStatus

router = APIRouter()


class EventObject(BaseModel):
    id: str
    status: PaymentStatus


class WebhookEvent(BaseModel):
    type: str
    event: str
    object: EventObject


@router.post("/{token}", tags=["webhook"])
async def webhook(token: str, event: WebhookEvent, db: SessionDep):
    if token != settings.WEBHOOK_TOKEN:
        raise HTTPException(status_code=404)
    payment_id = event.object.id
    payment = Payment.find_one(payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="not found")
    payment_status = PaymentStatus(payment.status)
    if payment_status != event.object.status:
        raise HTTPException(status_code=400)
    order = get_order_by_payment_id(db, payment_id)
    if not order:
        raise HTTPException(status_code=404, detail="not found")

    if (
        order.payment_status != payment_status
        and payment_status == PaymentStatus.SUCCEEDED
    ):
        msg = (
            f"Заказ {f'От @{order.user.username.replace('_', '\\_')}' if order.user.username else ''} оплачен\n\n"
            f'*Ссылка на заказавшего пользователя*: tg://user?id={order.user.tg_id}\n\n'
            f"*ФИО*: {order.fio}\n\n"
            f"*Адрес*: {order.address}\n\n"
            f"*Комментарий для доставки*: {order.address_details}\n\n"
            f"{f"*Транспортная компания*: {order.other_delivery_method.value}\n\n" if order.other_delivery_method else ''}"
            f"*Телефон*: {order.phone}\n\n"
            f"*email*: {order.receipt_email}\n\n"
            f"*Общая сумма*: {order.total_price}₽\n\n"
        )
        for order_item in order.items:
            msg += (
                f"{order_item.item.name}\n{order_item.item_size} - {order_item.quantity} шт"
                f" - {order_item.item_price * order_item.quantity}₽\n\n"
            )
        for admin_id in settings.ADMINS_IDS:
            await bot.send_message(admin_id, msg)
        send_email('info@wolfsblut.su', msg)
        # await bot.send_message(order.user.tg_id, 'ваш заказ оплачен и его данные уже поступили нашему менеджеру,')

    update_order_status(db, order, payment_status)
