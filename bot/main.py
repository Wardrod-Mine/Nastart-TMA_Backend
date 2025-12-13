import asyncio
import logging
import sys

from aiogram import Dispatcher
from aiogram.types import BotCommand

from bot.init_bot import bot
from bot.routers.admin import router as admin_router

dp = Dispatcher()


dp.include_router(admin_router)


async def main() -> None:
    await bot.set_my_commands(
        [BotCommand(command="start", description="Перезапустить бота")]
    )
    # await bot.send_message(7088093032, '[link](tg://user?id=782767277)', protect_content=False, parse_mode='Markdown')
    # tg://user?id=782767277
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
