from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from config import settings

router = Router()


class PostState(StatesGroup):
    waiting_for_post = State()
    waiting_for_button_text = State()


@router.message(F.text == "/admin")
async def admin_command(message: Message, state: FSMContext) -> None:
    await message.answer(
        "_Админка_ \n\n*/post*  -  Отправить пост с кнопкой в канал\n\n*/newproduct*"
        "  -  добавить товар\n\n*/products*  -  редактировать товары"
    )
    await state.clear()


@router.message(F.text == "/post")
async def post_command(message: Message, bot: Bot, state: FSMContext) -> None:
    await state.set_state(PostState.waiting_for_post)
    await bot.send_message(message.chat.id, "Отправьте текст поста одним сообщением")


@router.message(PostState.waiting_for_post)
async def post_text(message: Message, state: FSMContext) -> None:
    await state.update_data(message_id=message.message_id)
    await state.set_state(PostState.waiting_for_button_text)
    await message.answer("Оправьте текст который будет на кнопке под сообщением")


@router.message(PostState.waiting_for_button_text, F.text)
async def post(message: Message, bot: Bot, state: FSMContext) -> None:
    if not message.text:
        return
    data = await state.get_data()
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=message.text, url=settings.WEBAPP_URL),
            ]
        ]
    )
    await bot.copy_message(
        settings.CHANNEL_ID, message.chat.id, data["message_id"], reply_markup=kb
    )
    await bot.send_message(message.chat.id, "Пост отправлен")
    await state.clear()
