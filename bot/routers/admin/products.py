from aiogram import F, Router
from aiogram.types import (
    CallbackQuery,
    Message,
)
from sqlalchemy.orm import Session

from bot.keyboards import get_product_keyboard
from db.crud import get_first_item, get_item_by_id
from db.models import Item

router = Router()


def get_product_text(item: Item) -> str:
    return f"{item.name}\n\n*Размеры*: {'\n'.join(map(lambda size: f'{size.size} - {size.price}', item.sizes))}₽\n\nОписание: {item.description}\n"


@router.message(F.text == "/products")
async def products_command(message: Message, db: Session) -> None:
    item = get_first_item(db)
    if not item:
        await message.answer(
            "Нет добавленных товаров, Добавльте свой первый товар через */newproduct*"
        )
        return
    kb = get_product_keyboard(db, item)
    await message.answer(get_product_text(item), reply_markup=kb)


@router.callback_query(F.data.startswith("goto_item_"))
async def goto_item(callback: CallbackQuery, db: Session) -> None:
    if (
        callback.data is None
        or callback.message is None
        or not (isinstance(callback.message, Message))
    ):
        return
    item_id = int(callback.data.split("_")[2])
    item = get_item_by_id(db, item_id)
    if not item:
        await callback.answer("Товар не найден")
        return
    kb = get_product_keyboard(db, item)
    await callback.message.edit_text(get_product_text(item), reply_markup=kb)
