import asyncio
from aiogram import F, Bot, types, Router
from aiogram.types import (CallbackQuery, Message, KeyboardButton, 
                           ReplyKeyboardMarkup, LabeledPrice, PreCheckoutQuery)
from aiogram.fsm.context import FSMContext

from telegramBotCafe.utils.states import OrderProcess
from config import PAY, MANAGER
from telegramBotCafe.keyboards.reply_kb import back_to_main_menu, delivery_keyboard, delivery_or_pickup_kb, cash_or_card_kb
from telegramBotCafe.database.db_utils import (db_get_finally_cart_products, db_get_user_cart, 
                               db_clear_cart, db_get_user_info, db_save_order)


router = Router()


async def sending_report_to_manager(bot: Bot, chat_id: int, text: str):
    user = await db_get_user_info(chat_id)
    
    full_text = (
        f"{text}\n\n"
        f"👤 <b>Клієнт:</b> {user.name}\n"
        f"📞 <b>Контакт:</b> {user.phone or 'не вказано'}"
    )
    await bot.send_message(chat_id=MANAGER, text=full_text, parse_mode="HTML")


async def send_order_report_to_manager(
    bot: Bot, chat_id, data, cart_items, payment_status, products_sum, final_sum
):
    delivery_map = {
        "delivery": "Доставка кур'єром",
        "pickup": "Самовивіз",
        "self_delivery": "Самовивіз",
    }

    delivery_price = float(data.get("delivery_price", 0))
    raw_delivery_type = data.get("delivery_type")
    nice_delivery_type = delivery_map.get(raw_delivery_type, str(raw_delivery_type))

    if raw_delivery_type in ["self_delivery", "pickup"] or delivery_price == 0:
        delivery_info = "Безкоштовно (Самовивіз)"
    elif products_sum >= 500:
        delivery_info = "Безкоштовно (Акція 500+)"
    else:
        delivery_info = f"{delivery_price} UAH"

    to_pay_manager = 0 if "онлайн" in payment_status.lower() or "сплачено" in payment_status.lower() else final_sum

    report = (
        f"🔔 <b>НОВЕ ЗАМОВЛЕННЯ!</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>Клієнт ID:</b> <code>{chat_id}</code>\n"
        f"🚚 <b>Спосіб:</b> {nice_delivery_type}\n" 
        f"💰 <b>Статус оплати:</b> {payment_status}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📦 <b>Склад замовлення:</b>\n"
    )

    for item in cart_items:
        report += f"• {item.product_name} x{item.quantity} — {item.final_price} UAH\n"

    report += (
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🚚 <b>Доставка:</b> {delivery_info}\n"
        f"💰 <b>Товари:</b> {products_sum} UAH\n"
        f"🏁 <b>РАЗОМ ДО СПЛАТИ: {to_pay_manager} UAH</b>"
    )
    await sending_report_to_manager(bot, chat_id, report)


def get_order_details(data, cart_items):
    only_products_sum = sum(float(item.final_price) for item in cart_items)
    delivery_type = data.get("delivery_type")
    delivery_price = float(data.get("delivery_price", 0))
    final_amount = only_products_sum + delivery_price
    history_content = "\n".join([f"• {item.product_name} x{item.quantity}" for item in cart_items])
    
    if delivery_type in ["pickup", "self_delivery"] or delivery_price == 0:
        delivery_row = "🚀 <b>Самовивіз: БЕЗКОШТОВНО 🎉</b>"
    else:
        delivery_row = f"🚚 Доставка: <b>{delivery_price} UAH</b>"
        
    return {
        "only_products_sum": only_products_sum,
        "final_amount": final_amount,
        "history_content": history_content,
        "delivery_row": delivery_row,
        "delivery_type": delivery_type
    }


async def ask_payment_method(message: Message, state: FSMContext):
    await message.answer(
        "Оберіть спосіб оплати:",
        reply_markup=cash_or_card_kb()
    )
    await state.set_state(OrderProcess.choosing_payment)


@router.callback_query(F.data == "order_pay")
async def start_checkout(call: CallbackQuery, state: FSMContext):
    chat_id = call.from_user.id
    cart_items = await db_get_finally_cart_products(chat_id)

    if not cart_items:
        return await call.answer("😱 Ваш кошик порожній!", show_alert=True)

    await call.message.delete()
    await state.set_state(OrderProcess.choosing_delivery)

    await call.message.answer(
        "✨ <b>Оформлення!</b>\nОберіть спосіб отримання:",
        reply_markup=delivery_or_pickup_kb()
    )
    await call.answer()


@router.message(OrderProcess.choosing_delivery, F.text == "🚴🏼‍♂️ Самовивіз")
async def process_pickup(message: Message, state: FSMContext):
    await state.update_data(delivery_type="pickup", delivery_price=0)
    await message.answer("Ви обрали Самовивіз ✅\nАдреса: м. Київ, вул. Мирна, 23")
    await ask_payment_method(message, state)


@router.message(OrderProcess.choosing_delivery, F.text == "🚛 Доставка")
async def process_delivery_start(message: Message, state: FSMContext):
    await message.answer(
        "Надішліть геолокацію для доставки:",
        reply_markup=delivery_keyboard()
    )
    await state.set_state(OrderProcess.sending_location)


@router.message(OrderProcess.sending_location, F.location)
async def process_location(message: Message, state: FSMContext):
# TODO: uncomment this to avoid choosing locations outside Kyiv
    # lat = message.location.latitude
    # lon = message.location.longitude

    # Приблизний "квадрат" Києва: Lat (50.21 - 50.59), Lon (30.23 - 30.82)
    # is_inside_kyiv = 50.21 < lat < 50.59 and 30.23 < lon < 30.82
    # if not is_inside_kyiv:
    #     await message.answer(
    #         "🏙 На жаль, за вашими координатами ми бачимо, що ви поза межами Києва.\n"
    #         "Наша кур'єрська служба працює лише по місту.\n"
    #         "Ви можете обрати 'Самовивіз' або змінити адресу на київську!")
    #     return 

    chat_id = message.from_user.id
    items = await db_get_finally_cart_products(chat_id)

    actual_sum = sum(float(item.final_price) for item in items)
    delivery_price = 0 if actual_sum >= 500 else 100

    await state.update_data(
        delivery_type="delivery", 
        delivery_price=delivery_price, 
        total_cart_sum=actual_sum,
        #latitude=lat,
        #longitude=lon
    )
    
    msg = f"Вартість доставки: {delivery_price} UAH" if delivery_price > 0 else "Доставка: БЕЗКОШТОВНО 🎉"
    
    await message.answer(f"📍 Локацію отримано! {msg}")
    await ask_payment_method(message, state)


@router.message(F.text == "⬅️ Назад до вибору оплати")
async def back_to_payment_choice(message: Message, state: FSMContext):
    await message.answer(
        "Оберіть спосіб оплати ще раз:",
        reply_markup=cash_or_card_kb() 
    )

@router.message(
    OrderProcess.choosing_payment,
    F.text.in_(["💳 Оплата онлайн", "💵 Готівка"]))
async def final_order_confirmation(message: Message, state: FSMContext):
    chat_id = message.from_user.id
    payment_method = message.text
    data = await state.get_data()

    cart = await db_get_user_cart(chat_id)
    if not cart:
        await message.answer("⚠️ Сталася помилка з кошиком. Спробуйте ще раз")
        return

    cart_items = await db_get_finally_cart_products(chat_id)
    if not cart_items:
        await message.answer("⚠️ Кошик порожній")
        return

    res = get_order_details(data, cart_items)

    if payment_method == "💳 Оплата онлайн":

        back_pay_kb = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="⬅️ Назад до вибору оплати")]],
            resize_keyboard=True)

        test_payment_info = (
            "⏳ Генеруємо рахунок для оплати...\n\n"
            "🛠 <b>Інструкція для тестової оплати:</b>\n"
            "1. Натисніть кнопку 'Сплатити' двічі нижче\n"
            "2. Введіть номер: `4444333322221111`\n"
            "3. Термін дії: будь-яка дата в майбутньому (напр. 12/29)\n"
            "4. CVC: будь-які 3 цифри (напр. 123)\n\n"
            "💡 Це тестове середовище, реальні кошти не списуються"
        )
        await message.answer(
            test_payment_info,
            parse_mode="HTML",
            reply_markup=back_pay_kb
        )
        await asyncio.sleep(2)

        await message.bot.send_invoice(
            chat_id=chat_id,
            title="Оплата замовлення",
            description="Оплата замовлення в CafeSmile 🍰",
            payload=str(cart.id),
            provider_token=PAY,
            currency="UAH",
            prices=[
                LabeledPrice(
                    label="Замовлення",
                    amount=int(res['final_amount'] * 100)
                )
            ],
            start_parameter="cafe_order"
        )
    else:
        await db_save_order(
            user_id=chat_id,
            content=res['history_content'],
            total=res['final_amount'],
            delivery=res['delivery_type']
        )
        await message.answer(
            f"✅ <b>Замовлення прийнято!</b>\n\n"
            f"💰 Сума за товари: <b>{res['only_products_sum']} UAH</b>\n"
            f"{res['delivery_row']}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🏁 <b>ДО СПЛАТИ: {res['final_amount']} UAH</b>\n\n"
            f"📞 Очікуйте на повідомлення менеджера для підтвердження",
            reply_markup=back_to_main_menu(),
            parse_mode="HTML",
        )
        await send_order_report_to_manager(
            message.bot,
            chat_id,
            data,
            cart_items,
            "💵 Готівка",
            res['only_products_sum'],
            res['final_amount']
        )
        await db_clear_cart(cart.id)
        await state.clear()


@router.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_q: PreCheckoutQuery):
    await pre_checkout_q.answer(ok=True)


@router.message(F.successful_payment)
async def success_payment_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    chat_id = message.chat.id

    cart = await db_get_user_cart(chat_id)
    if not cart:
        await message.answer("⚠️ Помилка з кошиком після оплати. Зверніться до менеджера")
        return

    cart_items = await db_get_finally_cart_products(chat_id)
    if not cart_items:
        await message.answer("⚠️ Товари не знайдені. Зверніться до менеджера")
        return

    res = get_order_details(data, cart_items)

    await db_save_order(
        user_id=chat_id,
        content=res['history_content'],
        total=res['final_amount'],
        delivery=f"{res['delivery_type']} (ОПЛАЧЕНО ✅)"
    )
    await send_order_report_to_manager(
        message.bot,
        chat_id,
        data,
        cart_items,
        "💳 Сплачено онлайн ✅",
        res['only_products_sum'],
        0
    )
    await message.answer(
        f"💫 <b>Оплата успішна!</b>\n"
        f"✅ <b>Замовлення прийнято!</b>\n\n"
        f"💰 Сума за товари: <b>{res['only_products_sum']} UAH</b>\n"
        f"{res['delivery_row']}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🏁 <b>ДО СПЛАТИ: (СПЛАЧЕНО ✅)</b>\n\n"
        f"📞 Очікуйте на повідомлення менеджера!",
        reply_markup=back_to_main_menu(),
        parse_mode="HTML"
    )
    await db_clear_cart(cart.id)
    await state.clear()


