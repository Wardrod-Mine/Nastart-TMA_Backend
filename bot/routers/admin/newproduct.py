import os

from aiogram import Bot, F, Router
from PIL import Image as PILImage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery,
    Message,
)
from sqlalchemy.orm import Session

from bot.keyboards import end_creation_kb
from db.crud import create_product

router = Router()


class NewProductState(StatesGroup):
    input_name = State()
    # input_price = State()
    input_sizes = State()
    input_description = State()
    input_image = State()


# @router.message(F.document)
# async def asdf(message: Message, bot: Bot) -> None:
#     if not message.document:
#         return
#     await message.answer("DOC")
#     await message.answer(str(message.document.file_name))
#     file = await bot.get_file(message.document.file_id)
#     if not file.file_path:
#         return
#     # create ../media/photos/ if not exists
#     os.makedirs(os.path.join("../media/photos"), exist_ok=True)
#     await bot.download_file(file.file_path, f"../media/photos/{file.file_id}.jpg")
#     await message.answer(str(message.message_id))


# @router.message(F.photo)
# async def asd(message: Message, bot: Bot) -> None:
#     if not message.photo:
#         return
#     await message.answer("PHOTO " + str(message.caption))
#     file = await bot.get_file(message.photo[-1].file_id)
#     file2 = await bot.get_file(message.photo[0].file_id)
#     if not file.file_path:
#         return
#     if not file2.file_path:
#         return
#     # create ../media/photos/ if not exists
#     os.makedirs(os.path.join("../media/photos"), exist_ok=True)
#     await bot.download_file(file.file_path, f"../media/photos/{file.file_id}.jpg")
#     await bot.download_file(file2.file_path, f"../media/photos/{file2.file_id}.jpg")
#     await message.answer(str(message.message_id))


@router.message(F.text == "/newproduct")
async def newproduct_command(message: Message, state: FSMContext) -> None:
    await message.answer("Введите название товара")
    await state.set_state(NewProductState.input_name)


@router.message(NewProductState.input_name)
async def input_name(message: Message, state: FSMContext) -> None:
    name = message.text
    if not name:
        await message.answer("Введите название товара")
        return
    await state.update_data(name=name)
    await message.answer(
        "Введите новые размеры товара с их ценами по шаблону <размер>:<цена в рублях>\nНапример"
    )
    await message.answer("S:100\nM:200\nL:300")

    await state.set_state(NewProductState.input_sizes)


# @router.message(NewProductState.input_price)
# async def input_price(message: Message, state: FSMContext) -> None:
#     price = message.text
#     if not (price and price.isnumeric()):
#         await message.answer("Введите цену товара")
#         return
#     await state.update_data(price=int(price))
#     await message.answer("Введите описание товара")
#     await state.set_state(NewProductState.input_description)


@router.message(NewProductState.input_sizes)
async def input_sizes(message: Message, state: FSMContext, db: Session) -> None:
    sizes = message.text
    if not sizes:
        await message.answer("Введите размеры товара")
        return
    sizes = sizes.split("\n")
    prices = []
    try:
        for size in sizes:
            size, price = size.split(":")
            prices.append((size, int(price)))
    except ValueError:
        await message.answer("Ошибка в формате ввода")
        return
    await state.update_data(prices=prices)
    # update_item_sizes(db, item_id, prices)
    await message.answer("Введите описание товара")
    await state.set_state(NewProductState.input_description)


@router.message(NewProductState.input_description)
async def input_description(message: Message, state: FSMContext) -> None:
    description = message.text
    if not description:
        await message.answer("Введите описание товара")
        return
    await state.update_data(description=description)
    await message.answer("Отправьте картинками фотографии товара")
    await state.set_state(NewProductState.input_image)


@router.message(NewProductState.input_image)
async def input_image(message: Message, bot: Bot, state: FSMContext) -> None:
    photo = message.photo
    if not photo:
        await message.answer("Отправьте изображение товара")
        return
    file = await bot.get_file(photo[-1].file_id)
    if not file.file_path:
        return
    data = await state.get_data()
    image_paths = data.get("image_paths", []) + [(file.file_path, file.file_id)]
    await state.update_data(image_paths=image_paths)
    await message.answer(
        "Фото успешно добавлено, Вы можете отправить еще "
        "фотографий или завершить создание товара",
        reply_markup=end_creation_kb,
    )


@router.callback_query(NewProductState.input_image, F.data == "end_photos")
async def finish_creation(
    callback: CallbackQuery, bot: Bot, state: FSMContext, db: Session
):
    if not isinstance(callback.message, Message):
        return
    data = await state.get_data()
    name = data.get("name")
    description = data.get("description")
    prices = data.get("prices")
    image_paths = data.get("image_paths")
    if not (name and description and prices and image_paths):
        await state.clear()
        await bot.send_message(
            callback.from_user.id,
            "Не получилось создать товар\nНапишите /newproduct и попробуйте еще раз",
        )
        return
    urls = []
    os.makedirs(os.path.join("../media/photos"), exist_ok=True)

    for file_path, file_id in image_paths:
        # сохраняем с оригинальным расширением, если есть
        ext = os.path.splitext(file_path)[1] or ".jpg"
        raw_path = f"../media/photos/{file_id}{ext}"
        await bot.download_file(file_path, raw_path)
        # пытаемся открыть и конвертировать в JPG для совместимости
        try:
            im = PILImage.open(raw_path)
            rgb = im.convert("RGB")
            jpg_path = f"../media/photos/{file_id}.jpg"
            rgb.save(jpg_path, format="JPEG", quality=85)
            if raw_path != jpg_path and os.path.exists(raw_path):
                try:
                    os.remove(raw_path)
                except OSError:
                    pass
            urls.append(f"/photos/{file_id}.jpg")
        except Exception:
            # если не получилось конвертировать — используем оригинал
            urls.append(f"/photos/{file_id}{ext}")

    create_product(db, name, prices, description, urls)
    await state.clear()
    await callback.message.answer("Товар Успешно добавлен!")
