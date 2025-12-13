from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import Message

from config import settings
from db import SessionLocal


class AdminMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        message: Message,
        data: dict[str, Any],
    ) -> Any:
        if message.from_user is None:
            return
        if message.from_user.id in settings.ADMINS_IDS:
            return await handler(message, data)


class DatabaseMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        update: Any,
        data: dict[str, Any],
    ) -> Any:
        if update.from_user is None:
            return
        with SessionLocal() as db:
            data["db"] = db
            await handler(update, data)
