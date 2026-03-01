from typing import Union
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from telegramBotCafe.database.db_utils import (
    db_get_finally_cart_products,
    db_get_cart_item_by_id,
    db_update_quantity,
    db_delete_product
)
from telegramBotCafe.keyboards.inline_kb import generate_cart_keyboard
from telegramBotCafe.keyboards.reply_kb import back_to_main_menu


router = Router()


@router.callback_query(F.data == "Ваш кошик")
@router.message(F.text.contains("Кошик")) 
async def show_finally_cart(event: Union[CallbackQuery, Message]):
    chat_id = event.from_user.id

    cart_products = await db_get_finally_cart_products(chat_id)

    if not cart_products:
        text_empty = "😱 <b>Ваш кошик порожній</b>\nПоверніться до меню, щоб обрати щось смачненьке!"
        
        if isinstance(event, CallbackQuery):
            await event.message.delete()
            await event.message.answer(text_empty, reply_markup=back_to_main_menu())
            await event.answer() 
        else:
            await event.answer(text_empty, reply_markup=back_to_main_menu())
        return

    total_price = 0
    text = "<b>🧺 ВАШ КОШИК:</b>\n\n"

    for p in cart_products:
        item_price = float(p.final_price)
        total_price += item_price
        text += f"🔸 <b>{p.product_name}</b> — {p.quantity} шт.\n"

    text += "───────────────────\n"
    text += f"<b>💰 РАЗОМ: {total_price} UAH</b>\n"
    text += "❗️ Безкоштовна доставка від 500 UAH"

    reply_markup = generate_cart_keyboard(cart_products)

    if isinstance(event, CallbackQuery):
        if event.message.photo:
            await event.message.delete() 
            await event.message.answer(text, reply_markup=reply_markup)
        else:
            try:
                await event.message.edit_text(text, reply_markup=reply_markup)
            except Exception:

                await event.answer()
    else:
        await event.answer(text, reply_markup=reply_markup)


@router.callback_query(F.data.startswith("increase_"))
async def increase_quantity(call: CallbackQuery):
    finally_id = int(call.data.split("_")[1])
    await db_update_quantity(finally_id, 1)
    await show_finally_cart(call)


@router.callback_query(F.data.startswith("decrease_"))
async def decrease_quantity(call: CallbackQuery):
    finally_id = int(call.data.split("_")[1])
    item = await db_get_cart_item_by_id(finally_id)

    if item:
        if item.quantity > 1:
            await db_update_quantity(finally_id, -1)
            await show_finally_cart(call)
        else:
            await call.answer(
                "⚠️ Менше 1 шт. не можна!\nДля видалення натисніть ❌",
                show_alert=True,
            )
    else:
        await call.answer("❌ Товар не знайдено")


@router.callback_query(F.data.startswith("delete_"))
async def delete_cart_product(call: CallbackQuery):
    finally_id = int(call.data.split("_")[1])
    await db_delete_product(finally_id)
    await call.answer("Страву видалено з кошика❗️")
    await show_finally_cart(call)