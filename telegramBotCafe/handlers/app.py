import os
import asyncio
from os import getenv
from aiogram.types import PreCheckoutQuery
from pathlib import Path
from aiogram import Bot, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    CallbackQuery,
    FSInputFile,
    InputMediaPhoto,
    LabeledPrice,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from dotenv import load_dotenv, find_dotenv
from aiogram.fsm.context import FSMContext
from states import OrderProcess
from typing import Union
from database.db_utils import *
from keyboards.inline_kb import *
from keyboards.reply_kb import *
from utils.caption import *
from aiogram.types import FSInputFile


load_dotenv(find_dotenv())  # Автоматичний пошук .env

MEDIA_PATH = os.getenv("MEDIA_PATH")
if MEDIA_PATH:
    MEDIA_PATH = Path(MEDIA_PATH).resolve()
else:
    MEDIA_PATH = Path(
        "./media"
    ).resolve()  # Дефолтний шлях, якщо MEDIA_PATH немає в .env

TOKEN = os.getenv("TOKEN")
PAY = os.getenv("PORTMONE")
MANAGER = os.getenv("MANAGER")

router = Router()
bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode="HTML"))


def get_image_path(image_name):
    return MEDIA_PATH / image_name


@router.message(F.text == "✨ Головне меню")
async def handle_main_menu(message: Message):
    await message.answer(
        text="🏠 Ви повернулися до головного меню", reply_markup=generate_main_menu()
    )


@router.message(CommandStart())
async def command_start_handler(message: Message):
    await message.answer(
        "Приємного вибору! Обирай категорію страв нижче: 👇",
        reply_markup=generate_category_menu(message.from_user.id),
    )


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


async def start_register_user(message: Message):
    chat_id = message.chat.id
    full_name = message.from_user.full_name
    if db_register_user(full_name, chat_id):
        await message.answer(text="Авторизація пройшла успішно")
        await show_main_menu(message)
    else:
        await message.answer(
            text="Для зв'язку з Вами нам потрібний Ваш контактний номер",
            reply_markup=share_phone_button(),
        )


@router.message(F.contact)
async def update_user_info_finish_register(message: Message):
    chat_id = message.chat.id
    phone = message.contact.phone_number
    db_update_user(chat_id, phone)
    if db_create_user_cart(chat_id):
        await message.answer(text="Регістрація пройшла успішно!")

    await show_main_menu(message)


async def show_main_menu(message: Message):
    await message.answer(text="⬇️ Виберіть дію", reply_markup=generate_main_menu())


@router.message(F.text == "✅ Зробити замовлення")
async def make_order(message: Message):
    chat_id = message.chat.id
    await bot.send_message(
        chat_id=chat_id, text="🪄 Розпочнемо", reply_markup=back_to_main_menu()
    )
    await message.answer(
        text="🥡 Виберіть категорію", reply_markup=generate_category_menu(chat_id)
    )


@router.message(F.text == "✨ Головне меню")
async def return_to_main_menu(message: Message):
    try:
        await bot.delete_message(
            chat_id=message.chat.id, message_id=message.message_id - 1
        )
    except TelegramBadRequest:
        ...
    await show_main_menu(message)


@router.callback_query(F.data.startswith("category_"))
async def show_product_button(call: CallbackQuery):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    category_id = int(call.data.split("_")[-1])
    await bot.edit_message_text(
        text="🥢 Виберіть продукт",
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=show_product_by_category(category_id),
    )


@router.callback_query(F.data.startswith("product_"))
async def show_product_detail(call: CallbackQuery):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    product_id = int(call.data.split("_")[-1])

    product = db_get_product_by_id(product_id)
    if not product:
        return await call.answer("❌ Товар не знайдено!")
    category_id = product.category_id

    image_path = get_image_path(product.image.strip())

    await call.message.delete()

    if user_cart := db_get_user_cart(chat_id):
        text = text_for_caption(
            name=product.product_name,
            description=product.description,
            price=product.price,
            dish_weight=product.dish_weight,
        )

        await bot.send_photo(
            chat_id=chat_id,
            photo=FSInputFile(str(image_path)),
            caption=text,
            reply_markup=generate_constructor_button(
                quantity=1, category_id=category_id
            ),
        )
    else:
        await bot.send_message(
            chat_id=chat_id,
            text="😿 На жаль, у нас немає Вашого контакту",
            reply_markup=share_phone_button(),
        )
    await call.answer()


@router.callback_query(F.data.in_(["prod_plus", "prod_minus"]))
async def constructor_change(call: CallbackQuery):
    product_name = call.message.caption.split("\n")[0].strip()
    product = db_get_product_by_name(product_name)

    if not product:
        return await call.answer("❌ Товар не знайдено")

    current_qty = int(call.message.reply_markup.inline_keyboard[0][1].text)

    if call.data == "prod_plus":
        new_qty = current_qty + 1
    else:
        if current_qty <= 1:
            return await call.answer(
                "❗️ Менше одного вибрати не можна", show_alert=False
            )
        new_qty = current_qty - 1

    new_text = text_for_caption(
        name=product.product_name,
        description=product.description,
        price=product.price,
        dish_weight=product.dish_weight,
        quantity=new_qty,
    )

    await call.message.edit_caption(
        caption=new_text,
        reply_markup=generate_constructor_button(
            quantity=new_qty, category_id=product.category_id
        ),
        parse_mode="HTML",
    )
    await call.answer()


@router.callback_query(F.data.regexp(r"change_\d+_(plus|minus)"))
async def change_quantity(call: CallbackQuery):
    chat_id = call.from_user.id
    data = call.data.split("_")
    finally_id = int(data[1])
    action = data[2]

    item = db_session.execute(
        select(FinallyCarts).where(FinallyCarts.id == finally_id)
    ).scalar_one_or_none()

    if not item:
        await bot.answer_callback_query(call.id, text="❌ Продукт не знайдено!")
        return

    if action == "plus":
        item.quantity += 1
    elif action == "minus" and item.quantity > 1:
        item.quantity -= 1
    else:
        await bot.answer_callback_query(call.id, text="❌ Мінімальна кількість 1")
        return

    db_session.commit()
    await bot.answer_callback_query(call.id, text="Кількість змінена")
    await show_finally_cart(call)


@router.callback_query(F.data == "put_into_cart")
async def put_into_cart_handler(call: CallbackQuery):
    chat_id = call.message.chat.id
    quantity = int(call.message.reply_markup.inline_keyboard[0][1].text)
    product_name = call.message.caption.split("\n")[0].strip()

    product = db_get_product_by_name(product_name)
    user_cart = db_get_user_cart(chat_id)

    if product and user_cart:
        db_add_to_finally_cart(
            cart_id=user_cart.id,
            product_name=product.product_name,
            price=product.price,
            quantity=quantity,
        )
        await call.answer(f"✅ {product_name} додано!")

        await call.message.delete()

        await call.message.answer(
            text="✅ Товар додано! Виберіть наступну категорію:",
            reply_markup=generate_category_menu(
                chat_id
            ),  
        )
    else:
        await call.answer("❌ Помилка додавання", show_alert=True)


@router.callback_query(F.data == "back_from_product")
async def back_from_product(call: CallbackQuery):
    await call.message.delete()

    await bot.send_message(
        chat_id=call.from_user.id,
        text="<b>📂 Оберіть категорію:</b>",
        reply_markup=generate_category_menu(call.from_user.id),
        parse_mode="HTML",
    )
    await call.answer()


@router.callback_query(F.data == "Ваш кошик")
@router.message(F.text.contains("Кошик")) 
async def show_finally_cart(event: Union[CallbackQuery, Message]):
    chat_id = event.from_user.id

    cart_products = db_get_finally_cart_products(chat_id)

    if not cart_products:
        text_empty = "😱 Ваш кошик порожній"
        if isinstance(event, CallbackQuery):
            await event.message.delete()
            await event.message.answer(text_empty)
        else:
            await event.answer(text_empty)
        return

    builder = InlineKeyboardBuilder()

    total_price = 0
    text = "<b>🛒 ВАШ КОШИК:</b>\n\n"

    for p in cart_products:
        item_price = float(p.final_price)
        total_price += item_price

        # 1. Залишаємо назву в основному тексті повідомлення (як список)
        text += f"🔸 <b>{p.product_name}</b> — {p.quantity} шт.\n"
        # Рядок-заголовок (кнопка, яка не реагує на клік)
        # Ми додаємо пробіли або символи, щоб вона виглядала як розділювач
        builder.row(
            InlineKeyboardButton(text=f"🔷 {p.product_name}", callback_data="ignore")
        )

        # 3. Кнопки керування прямо під ним
        builder.row(
            InlineKeyboardButton(text="➖", callback_data=f"decrease_{p.id}"),
            InlineKeyboardButton(text=f"{p.quantity} шт.", callback_data="ignore"),
            InlineKeyboardButton(text="➕", callback_data=f"increase_{p.id}"),
            InlineKeyboardButton(text="❌", callback_data=f"delete_{p.id}"),
        )

    text += "───────────────────\n"
    text += f"<b>💰 РАЗОМ: {total_price} UAH</b>\n"
    text += "❗️ Безкоштовна доставка від 500 UAH"

    builder.row(
        InlineKeyboardButton(text="🚀 Оформити замовлення", callback_data="order_pay")
    )
    builder.row(
        InlineKeyboardButton(
            text="🔙 Повернутися в меню", callback_data="return_to_category"
        )
    )

    if isinstance(event, CallbackQuery):
        if event.message.photo:
            await event.message.delete() 
            await event.message.answer(
                text, reply_markup=builder.as_markup(), parse_mode="HTML"
            )
        else:
            try:
                await event.message.edit_text(
                    text, reply_markup=builder.as_markup(), parse_mode="HTML"
                )
            except Exception:
                await event.answer()
    else:
        await event.answer(text, reply_markup=builder.as_markup(), parse_mode="HTML")


@router.callback_query(F.data.regexp(r"delete_\d+"))
async def delete_cart_product(call: CallbackQuery):
    # Delete buttons ❌
    finally_id = int(call.data.split("_")[-1])
    db_delete_product(finally_id)
    await bot.answer_callback_query(
        callback_query_id=call.id, text="Продукт видалено з кошика❗️"
    )
    await show_finally_cart(call)


@router.callback_query(F.data == "order_pay")
async def start_checkout(call: CallbackQuery, state: FSMContext):
    chat_id = call.from_user.id

    cart_items = db_get_finally_cart_products(chat_id)

    if not cart_items:
        return await call.answer("🛒 Ваш кошик порожній!", show_alert=True)

    await call.message.delete()

    await state.set_state(OrderProcess.choosing_delivery)

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🚛 Доставка"), KeyboardButton(text="🚴🏼‍♂️ Самовивіз")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    await call.message.answer(
        "✨ <b>Починаємо оформлення!</b>\nОберіть, як ви хочете отримати замовлення:",
        reply_markup=keyboard,
        parse_mode="HTML",
    )
    await call.answer()


async def sending_report_to_manager(chat_id: int, text: str):
    user = db_get_user_info(chat_id)
    text += f"\n\nІм'я клієнта: {user.name}\nКонтакт: {user.phone or 'не вказано'}\n"
    await bot.send_message(chat_id=MANAGER, text=text)


@router.callback_query(F.data.startswith("increase_"))
async def increase_quantity(call: CallbackQuery):
    finally_id = int(call.data.split("_")[1])
    db_update_quantity(finally_id, 1)

    await show_finally_cart(call)


@router.callback_query(F.data.startswith("decrease_"))
async def decrease_quantity(call: CallbackQuery):
    finally_id = int(call.data.split("_")[1])

    item = db_get_cart_item_by_id(finally_id)

    if item:
        if item.quantity > 1:
            db_update_quantity(finally_id, -1)
            await show_finally_cart(call)
        else:
            await call.answer(
                "⚠️ Менше 1 шт. не можна!\nЯкщо хочете видалити товар — натисніть на смітник 🗑",
                show_alert=True,
            )
    else:
        await call.answer("❌ Товар не знайдено в кошику")


@router.callback_query(F.data.startswith("delete_"))
async def delete_cart_product(call: CallbackQuery):
    finally_id = int(call.data.split("_")[1])
    db_delete_product(finally_id)

    await call.answer("Продукт видалено з кошика❗️")
    await show_finally_cart(call)


@router.callback_query(F.data.startswith("back_to_list_"))
async def back_to_products_list(call: CallbackQuery):
    category_id = int(call.data.split("_")[-1])

    await call.message.delete()

    await bot.send_message(
        chat_id=call.from_user.id,
        text="🥢 Виберіть продукт",
        reply_markup=show_product_by_category(category_id),
    )
    await call.answer()


@router.callback_query(F.data == "return_to_category")
async def back_to_categories_menu(call: CallbackQuery):

    chat_id = call.from_user.id

    await call.message.delete()

    await call.message.answer(
        text="🥡 Виберіть категорію:",
        reply_markup=generate_category_menu(chat_id),
    )
    await call.answer()


@router.message(OrderProcess.choosing_delivery, F.text == "🚴🏼‍♂️ Самовивіз")
async def process_pickup(message: Message, state: FSMContext):
    await state.update_data(delivery_type="pickup", delivery_price=0)

    await message.answer("Ви обрали Самовивіз ✅\nАдреса: м. Київ, вул. Мирна, 23.")
    await ask_payment_method(message, state)


@router.message(OrderProcess.choosing_delivery, F.text == "🚛 Доставка")
async def process_delivery_start(message: Message, state: FSMContext):
    location_button = KeyboardButton(
        text="Відправити геолокацію 📍", request_location=True
    )
    keyboard = ReplyKeyboardMarkup(keyboard=[[location_button]], resize_keyboard=True)

    await message.answer(
        "Будь ласка, надішліть геолокацію для доставки:", reply_markup=keyboard
    )
    await state.set_state(OrderProcess.sending_location)


@router.message(OrderProcess.sending_location, F.location)
async def process_location(message: Message, state: FSMContext):
    chat_id = message.chat.id

    items = db_get_finally_cart_products(chat_id)

    actual_sum = 0.0
    for row in items:
        actual_sum += float(row[3])

    if actual_sum >= 500:
        delivery_price = 0
    else:
        delivery_price = 100

    await state.update_data(
        delivery_type="delivery",
        delivery_price=delivery_price,
        total_cart_sum=actual_sum,
    )

    msg = (
        f"Вартість доставки: {delivery_price} UAH"
        if delivery_price > 0
        else "Доставка: БЕЗКОШТОВНО 🎉"
    )
    await message.answer(f"📍 Геолокацію отримано!\n{msg}")

    await ask_payment_method(message, state)


async def ask_payment_method(message: Message, state: FSMContext):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="💳 Оплата онлайн"), KeyboardButton(text="💵 Готівка")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    await message.answer("Оберіть спосіб оплати:", reply_markup=keyboard)
    await state.set_state(OrderProcess.choosing_payment)


@router.message(OrderProcess.choosing_payment)
async def final_order_confirmation(message: Message, state: FSMContext):
    chat_id = message.from_user.id
    payment_method = message.text
    data = await state.get_data()

    cart = db_get_user_cart(chat_id)
    cart_items = db_get_finally_cart_products(chat_id)

    if not cart or not cart_items:
        await message.answer("🛒 Сталася помилка: кошик порожній.")
        await state.clear()
        return

    only_products_sum = 0.0
    for item in cart_items:
        only_products_sum += float(item[3])

    delivery_type = data.get("delivery_type")
    delivery_price = float(data.get("delivery_price", 0))
    final_amount = only_products_sum + delivery_price

    if delivery_type == "self_delivery" or delivery_price == 0:
        delivery_row = "🚀 <b>Самовивіз: БЕЗКОШТОВНО 🎉</b>"
    elif only_products_sum >= 500:

        delivery_row = "🚚 Доставка: <b>БЕЗКОШТОВНО 🎉</b>"
    else:

        delivery_row = f"🚚 Доставка: <b>{delivery_price} UAH</b>"

    if payment_method == "💳 Оплата онлайн":
        await message.answer(
            "Генеруємо рахунок для оплати...", reply_markup=ReplyKeyboardRemove()
        )

        await asyncio.sleep(1.5)

        amount_in_cents = int(final_amount * 100)

        await bot.send_invoice(
            chat_id=chat_id,
            title="Оплата замовлення",
            description="Смачненьке вже готується! 🍕",
            payload=str(cart.id),
            provider_token=PAY,
            currency="UAH",
            prices=[LabeledPrice(label="Замовлення", amount=amount_in_cents)],
            start_parameter="cafe_order",
        )

    else:
        await message.answer(
            f"✅ <b>Замовлення прийнято!</b>\n\n"
            f"💰 Сума за товари: <b>{only_products_sum} UAH</b>\n"
            f"{delivery_row}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🏁 <b>РАЗОМ ДО СПЛАТИ: {final_amount} UAH</b>\n\n"
            f"📞 Очікуйте на повідомлення менеджера для підтвердження.",
            reply_markup=back_to_main_menu(),
            parse_mode="HTML",
        )

        await send_order_report_to_manager(
            chat_id=chat_id,
            data=data,
            cart_items=cart_items,
            payment_status="💵 Готівка",
            products_sum=only_products_sum,
            final_sum=final_amount, 
        )

        db_session.execute(delete(FinallyCarts).where(FinallyCarts.cart_id == cart.id))
        db_session.commit()

        await state.clear()


async def send_order_report_to_manager(
    chat_id, data, cart_items, payment_status, products_sum, final_sum
):
    delivery_map = {
        "delivery": "Доставка кур'єром",
        "pickup": "Самовивіз",
        "self_delivery": "Самовивіз",
    }

    delivery_price = float(data.get("delivery_price", 0))
    raw_delivery_type = data.get("delivery_type")

    nice_delivery_type = delivery_map.get(raw_delivery_type, raw_delivery_type)

    if raw_delivery_type in ["self_delivery", "pickup"] or delivery_price == 0:
        delivery_info = "Безкоштовно (Самовивіз)"
    elif products_sum >= 500:
        delivery_info = "Безкоштовно (Акція 500+)"
    else:
        delivery_info = f"{delivery_price} UAH"

    report = f"🔔 <b>НОВЕ ЗАМОВЛЕННЯ!</b>\n"
    report += f"━━━━━━━━━━━━━━━━━━\n"
    report += f"👤 <b>Клієнт:</b> <a href='tg://user?id={chat_id}'>Контакт</a> (ID: {chat_id})\n"
    report += f"🚚 <b>Спосіб:</b> {nice_delivery_type}\n" 
    report += f"💰 <b>Статус оплати:</b> {payment_status}\n"
    report += f"━━━━━━━━━━━━━━━━━━\n"
    report += f"📦 <b>Склад замовлення:</b>\n"

    for item in cart_items:
        report += f"• {item[1]} x{item[2]} — {item[3]} UAH\n"

    report += f"━━━━━━━━━━━━━━━━━━\n"
    report += f"🚚 <b>Доставка:</b> {delivery_info}\n"
    report += f"💰 <b>Товари:</b> {products_sum} UAH\n"
    report += f"🏁 <b>РАЗОМ ДО СПЛАТИ: {final_sum} UAH</b>"

    await sending_report_to_manager(chat_id, report)


@router.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_q: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)


@router.message(F.successful_payment)
async def success_payment_handler(message: Message, state: FSMContext):
    chat_id = message.chat.id

    data = await state.get_data()

    cart_items = db_get_finally_cart_products(chat_id)
    cart = db_get_user_cart(chat_id)

    await send_order_report_to_manager(
        chat_id=chat_id,
        data=data,
        cart_items=cart_items,
        payment_status="💳 ОПЛАЧЕНО (Онлайн)",
        products_sum=only_products_sum,
        final_sum=final_amount,  
    )

    await message.answer(
        f"✨ <b>Оплата успішна!</b>\n\n"
        f"✅ Ми отримали <b>{total_paid} UAH</b>.\n"
        f"👨‍🍳 Кухня вже готує ваше замовлення.\n\n"
        f"📝 Менеджер може зателефонувати вам для уточнення деталей доставки.",
        reply_markup=back_to_main_menu(),
        parse_mode="HTML",
    )

    if cart:
        db_session.execute(delete(FinallyCarts).where(FinallyCarts.cart_id == cart.id))
        db_session.commit()

    await state.clear()
