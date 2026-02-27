from aiogram import Router, F, types
from aiogram.types import Message
from telegramBotCafe.database.db_utils import db_get_user_history


router = Router()


@router.message(F.text == "📌 Важлива інформація")
async def important_info_handler(message: Message):

    text = (
        "<b>🏪 Інформація для клієнтів</b>\n"
        "───────────────────\n\n"
        "<b>🕒 Режим роботи:</b>\n"
        "Пн–Пт: 09:00 – 20:00\n"
        "Сб–Нд: 10:00 – 22:00\n\n"
        "<b>📍 Адреса:</b>\n"
        "м. Київ, вул. Мирна 23\n"
        "Самовивіз - доступний\n\n"
        "<b>🚚 Доставка:</b>\n"
        "Від 500 грн — безкоштовна\n"
        "До 500 грн — 100 грн по місту\n\n"
        "<b>🎁 Бонуси:</b>\n"
        "-20% у день народження 🎂\n"
        "Подарунок при замовленні від 1000 грн (напій на вибір)\n\n"
        "<b>💳 Оплата:</b>\n"
        "Карткою / Готівкою / Онлайн"
    )

    await message.answer(text)


@router.message(F.text == "📜 Мої замовлення")
async def show_order_history(message: Message):
    history = await db_get_user_history(message.from_user.id, limit=5)
    
    if not history:
        await message.answer("💬 Ви ще нічого не замовляли у нас. Оберіть щось смачненьке в меню! 🍕")
        return

    response = "<b>📦 Ваші останні замовлення:</b>\n\n"
    for order in history:
        date_str = order.created_at.strftime("%d.%m.%Y %H:%M")
        response += (
            f"📅 <b>{date_str}</b>\n"
            f"{order.order_content}\n"
            f"💰 Разом: <b>{order.total_amount} UAH</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
        )
    
    await message.answer(response, parse_mode="HTML")