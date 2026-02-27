from aiogram import Router, types, F
from aiogram.filters import CommandStart

from telegramBotCafe.database.db_utils import (
    db_register_user,
    db_update_user,
    db_create_user_cart,
    db_get_user_info,
    db_get_all_category,
    db_get_finally_price
)
from telegramBotCafe.keyboards.reply_kb import share_phone_button, generate_main_menu
from telegramBotCafe.keyboards.inline_kb import generate_category_menu


start_router = Router()


@start_router.message(CommandStart())
async def cmd_start(message: types.Message):
    chat_id = message.from_user.id
    full_name = message.from_user.full_name

    user_exists = await db_register_user(full_name, chat_id)

    if not user_exists:
        await db_create_user_cart(chat_id)
        await message.answer(
            f"Вітаємо у SMILE😊, {message.from_user.first_name}!\n"
            "Для завершення реєстрації нам потрібен Ваш контактний номер:",
            reply_markup=share_phone_button(),
        )
    else:
        categories = await db_get_all_category()
        total_price = await db_get_finally_price(chat_id)

        await message.answer(
            "Раді бачити вас знову! 😊\nОбирайте категорію нижче: 👇",
            reply_markup=generate_category_menu(categories, total_price),
        )


@start_router.message(F.contact)
async def update_user_info_finish_register(message: types.Message):
    chat_id = message.from_user.id
    phone = message.contact.phone_number

    await db_update_user(chat_id, phone)

    categories = await db_get_all_category()
    total_price = await db_get_finally_price(chat_id)

    await message.answer(
        text="Реєстрація пройшла успішно! ✅",
        reply_markup=generate_main_menu(),
    )


@start_router.message(F.text == "✨ Головне меню")
async def handle_main_menu(message: types.Message):
    await message.answer(
        text="🏠 Ви повернулися до головного меню", reply_markup=generate_main_menu()
    )


async def show_main_menu(message: types.Message):
    await message.answer(text="⬇️ Виберіть дію", reply_markup=generate_main_menu())
