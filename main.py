import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from config import TOKEN
from telegramBotCafe.handlers import routers
from telegramBotCafe.database.engine import engine
from telegramBotCafe.database.base import Base 
from telegramBotCafe.database.models import (
    Users,
    Categories,
    Products,
    Carts,
    FinallyCarts,
    Orders,
)


async def main():
    logging.basicConfig(level=logging.INFO)

    logging.info("Ініціалізація бази данних...")
    try:
        async with engine.begin() as conn:

            await conn.run_sync(Base.metadata.create_all)
        logging.info("База данних успішно готова!")
    except Exception as e:
        logging.error(f"Помилка при створенні таблиць: {e}")
        return 

    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
    dp = Dispatcher()
    dp.include_routers(*routers)

    await bot.delete_webhook(drop_pending_updates=True)
    
    logging.info("Бот запускається...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот вимкнено")