from aiogram.utils.keyboard import ReplyKeyboardBuilder, ReplyKeyboardMarkup
from aiogram.types import KeyboardButton


def share_phone_button() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="☎️ Надіслати свій контакт 📞", request_contact=True)
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


def generate_main_menu() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="✅ Зробити замовлення")
    builder.button(text="🧺 Кошик")
    builder.button(text="📌 Важлива інформація")
    builder.button(text="📜 Мої замовлення")
    builder.adjust(2, 2) 
    return builder.as_markup(resize_keyboard=True)


def delivery_or_pickup_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="🚛 Доставка")
    builder.button(text="🚴🏼‍♂️ Самовивіз")
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


def cash_or_card_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="💳 Оплата онлайн")
    builder.button(text="💵 Готівка")
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


def back_to_main_menu() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="✨ Головне меню")
    return builder.as_markup(resize_keyboard=True)


def back_and_main_menu_buttons() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="🧺 Кошик")
    builder.button(text="✨ Головне меню") 
    builder.adjust(2) 
    return builder.as_markup(resize_keyboard=True)


def delivery_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="Відправити геолокацію 📍", request_location=True)
    builder.button(text="✨ Головне меню")
    builder.adjust(1, 1)
    return builder.as_markup(resize_keyboard=True)