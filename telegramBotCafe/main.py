import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv, find_dotenv

from handlers.app import router

load_dotenv(find_dotenv())

TOKEN = os.getenv('TOKEN')
PAY = os.getenv('PORTMONE')
MANAGER = os.getenv('MANAGER')
dp = Dispatcher()
bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode='HTML'))

dp.include_router(router)


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())

