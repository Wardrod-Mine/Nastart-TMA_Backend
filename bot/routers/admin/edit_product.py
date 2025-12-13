import os

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery,
    Message,
)
from sqlalchemy.orm import Session

from bot.keyboards import (
    categories_kb,
    edit_product_keyboard,
    end_photos_kb,
    flavours_kb,
)
from db.crud import (
    delete_item,
    get_item_by_id,
    update_item_category,
    update_item_description,
    update_item_flavour,
    update_item_images,
    update_item_name,
    update_item_sizes,
)
from db.models import ProductCategory, ProductFlavour

router = Router()


class EditState(StatesGroup):
    input_name = State()
    input_price = State()
    input_flavour = State()
    input_category = State()
    input_sizes = State()
    input_description = State()
    input_image = State()


@router.callback_query(F.data.startswith("delete_item_"))
async def delete_item_handler(callback: CallbackQuery, db: Session) -> None:
    if not callback.data or not isinstance(callback.message, Message):
        return
    item_id = int(callback.data.split("_")[2])
    delete_item(db, item_id)
    await callback.message.answer("Товар успешно удален!")
    await callback.message.delete()


@router.callback_query(F.data.startswith("edit_item_"))
async def edit_item(callback: CallbackQuery, db: Session) -> None:
    if not callback.data or not isinstance(callback.message, Message):
        return
    item_id = int(callback.data.split("_")[2])
    item = get_item_by_id(db, item_id)
    if not item:
        await callback.answer("Товар не найден")
        return
    msg = (
        f"*Назвние*: {item.name}\n\n*Размеры*: {'\n'.join(map(lambda size: f'{size.size} - {size.price}', item.sizes))}₽\n\n"
        f"*Описание*: {item.description}\n"
    )

    await callback.message.answer(msg, reply_markup=edit_product_keyboard(item_id))


@router.callback_query(F.data.startswith("edit_"))
async def edit_name(callback: CallbackQuery, db: Session, state: FSMContext) -> None:
    if not callback.data or not isinstance(callback.message, Message):
        return
    item_id = int(callback.data.split("_")[2])
    to_edit = callback.data.split("_")[1]
    if to_edit == "name":
        await state.set_state(EditState.input_name)
        await callback.message.answer("Введите новое название товара")
    elif to_edit == "price":
        await state.set_state(EditState.input_price)
        await callback.message.answer("Введите новую цену товара")
    elif to_edit == "flavour":
        await state.set_state(EditState.input_flavour)
        await callback.message.answer(
            "Выберите новый вкус товара", reply_markup=flavours_kb
        )
    elif to_edit == "category":
        await state.set_state(EditState.input_category)
        await callback.message.answer(
            "Выберите новую категорию товара", reply_markup=categories_kb
        )
    elif to_edit == "sizes":
        await state.set_state(EditState.input_sizes)
        await callback.message.answer(
            "Введите новые размеры товара с их ценами по шаблону <размер>:<цена в рублях>\nНапример"
        )
        await callback.message.answer("S:100\nM:200\nL:300")

    elif to_edit == "description":
        await state.set_state(EditState.input_description)
        await callback.message.answer("Введите новое описание товара")
    elif to_edit == "images":
        await state.set_state(EditState.input_image)
        await callback.message.answer("Отправьте новые фотографии товара")
    await state.update_data(item_id=item_id)


@router.message(EditState.input_name)
async def input_name(message: Message, state: FSMContext, db: Session) -> None:
    name = message.text
    if not name:
        await message.answer("Введите название товара")
        return
    data = await state.get_data()
    item_id = data.get("item_id")
    if not item_id:
        await message.answer("Произошла ошибка")
        await state.clear()
        return
    update_item_name(db, item_id, name)
    await message.answer("Название успешно изменено")
    await state.clear()


# @router.message(EditState.input_price)
# async def input_price(message: Message, state: FSMContext, db: Session) -> None:
#     price = message.text
#     if not (price and price.isnumeric()):
#         await message.answer("Введите цену товара")
#         return
#     data = await state.get_data()
#     item_id = data.get("item_id")
#     if not item_id:
#         await message.answer("Произошла ошибка")
#         await state.clear()
#         return
#     update_item_price(db, item_id, int(price))
#     await message.answer("Цена успешно изменена")
#     await state.clear()


@router.message(EditState.input_sizes)
async def input_sizes(message: Message, state: FSMContext, db: Session) -> None:
    sizes = message.text
    if not sizes:
        await message.answer("Введите размеры товара")
        return
    data = await state.get_data()
    item_id = data.get("item_id")
    if not item_id:
        await message.answer("Произошла ошибка")
        await state.clear()
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
    update_item_sizes(db, item_id, prices)
    await message.answer("Размеры успешно изменены")
    await state.clear()


@router.message(EditState.input_description)
async def input_description(message: Message, state: FSMContext, db: Session) -> None:
    description = message.text
    if not description:
        await message.answer("Введите описание товара")
        return
    data = await state.get_data()
    item_id = data.get("item_id")
    if not item_id:
        await message.answer("Произошла ошибка")
        await state.clear()
        return
    update_item_description(db, item_id, description)
    await message.answer("Описание успешно изменено")
    await state.clear()


@router.message(EditState.input_image)
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
        "фотографий или завершить изменение фотографий",
        reply_markup=end_photos_kb,
    )


@router.callback_query(EditState.input_image, F.data == "end_photos")
async def finish_photos(
    callback: CallbackQuery, bot: Bot, state: FSMContext, db: Session
):
    if not isinstance(callback.message, Message):
        return
    data = await state.get_data()
    item_id = data.get("item_id")
    if not item_id:
        await state.clear()
        return
    image_paths = data.get("image_paths")
    if not (image_paths):
        await state.clear()
        return
    urls = []
    os.makedirs(os.path.join("../media/photos"), exist_ok=True)

    for file_path, file_id in image_paths:
        await bot.download_file(file_path, f"../media/photos/{file_id}.jpg")
        urls.append(f"/photos/{file_id}.jpg")

    update_item_images(db, item_id, urls)

    await state.clear()
    await callback.message.answer("Картинки Успешно обновлены!")


@router.callback_query(EditState.input_flavour)
async def input_flavour(
    callback: CallbackQuery, db: Session, state: FSMContext
) -> None:
    if not callback.data or not isinstance(callback.message, Message):
        return
    flavour = callback.data
    if not flavour:
        await callback.message.answer("Введите вкус товара")
        return
    if flavour not in ProductFlavour.__members__:
        await callback.message.answer("Выберите вкус товара")
    data = await state.get_data()
    item_id = data.get("item_id")
    if not item_id:
        await callback.message.answer("Произошла ошибка")
        await state.clear()
        return
    update_item_flavour(db, item_id, ProductFlavour[flavour])
    await callback.message.answer("Вкус успешно изменен")
    await state.clear()


@router.callback_query(EditState.input_category)
async def input_category(
    callback: CallbackQuery, db: Session, state: FSMContext
) -> None:
    if not callback.data or not isinstance(callback.message, Message):
        return
    category = callback.data
    if not category:
        await callback.message.answer("Введите категорию товара")
        return
    if category not in ProductCategory.__members__:
        await callback.message.answer("Выберите категорию товара")
    data = await state.get_data()
    item_id = data.get("item_id")
    if not item_id:
        await callback.message.answer("Произошла ошибка")
        await state.clear()
        return
    update_item_category(db, item_id, ProductCategory[category])
    await callback.message.answer("Категория успешно изменена")
    await state.clear()
