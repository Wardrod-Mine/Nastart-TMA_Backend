from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy.orm import Session

from db.crud import get_prev_and_next_items
from db.models import Item


def get_product_keyboard(db: Session, imem: Item) -> InlineKeyboardMarkup:
    prev_id, next_id = get_prev_and_next_items(db, imem)
    kb = []
    if prev_id:
        kb.append(InlineKeyboardButton(text="⬅️", callback_data=f"goto_item_{prev_id}"))
    if next_id:
        kb.append(InlineKeyboardButton(text="➡️", callback_data=f"goto_item_{next_id}"))
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Редактировать ✍️", callback_data=f"edit_item_{imem.id}"
                )
            ],
            # [
            #     InlineKeyboardButton(
            #         text="Статистика 📈", callback_data=f"view_stats_{imem.id}"
            #     )
            # ],
            [
                InlineKeyboardButton(
                    text="Удалить 🗑️", callback_data=f"delete_item_{imem.id}"
                )
            ],
            # [
            #     InlineKeyboardButton(
            #         text="Сделать пост с ссылкой 🔗",
            #         callback_data=f"make_post_{imem.id}",
            #     )
            # ],
            kb,
        ]
    )


def edit_product_keyboard(item_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Изменить название", callback_data=f"edit_name_{item_id}"
                )
            ],
            # [
            #     InlineKeyboardButton(
            #         text="Изменить цену", callback_data=f"edit_price_{item_id}"
            #     )
            # ],
            [
                InlineKeyboardButton(
                    text="Изменить Вкус",
                    callback_data=f"edit_flavour_{item_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="Изменить Категорию",
                    callback_data=f"edit_category_{item_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="Изменить размеры и цены",
                    callback_data=f"edit_sizes_{item_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="Изменить описание",
                    callback_data=f"edit_description_{item_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="Изменить фотографии",
                    callback_data=f"edit_images_{item_id}",
                )
            ],
        ]
    )


flavours_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Баранина", callback_data="BARANINA"),
        ],
        [
            InlineKeyboardButton(text="Индейка", callback_data="INDEYKA"),
        ],
        [
            InlineKeyboardButton(text="Оленина", callback_data="OLENINA"),
        ],
        [
            InlineKeyboardButton(text="Утка", callback_data="YTKA"),
        ],
    ]
)

categories_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Щенки", callback_data="PUPPIES"),
        ],
        [
            InlineKeyboardButton(
                text="Взрослые кошки (1+ лет)", callback_data="CATS_1"
            ),
        ],
        [
            InlineKeyboardButton(
                text="Взрослые собаки (1-6 лет)", callback_data="DOGS_1_6"
            ),
        ],
        [
            InlineKeyboardButton(
                text="Взрослые собаки (7+ лет)", callback_data="DOGS_7"
            ),
        ],
        [
            InlineKeyboardButton(
                text="Запеченный корм для собак всех возрастов",
                callback_data="ZAPECHENIY",
            ),
        ],
    ]
)

end_creation_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Создать товар", callback_data="end_photos")]
    ]
)
end_photos_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Сохранить", callback_data="end_photos")]
    ]
)
