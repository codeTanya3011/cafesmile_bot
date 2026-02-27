from aiogram.fsm.state import StatesGroup, State


class OrderProcess(StatesGroup):
    choosing_delivery = State() # доставка / самовивіз
    sending_location = State()  # очікування гео
    choosing_payment = State()  # карта / готівка