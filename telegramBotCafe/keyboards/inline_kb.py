from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup, InlineKeyboardButton

from database.db_utils import (db_get_all_category, db_get_products,
                                               db_get_finally_price, db_get_product_for_delete)


def generate_category_menu(chat_id: int) -> InlineKeyboardMarkup:
    total_price = db_get_finally_price(chat_id)
    categories = db_get_all_category() # Тягнемо всі категорії з бази
    builder = InlineKeyboardBuilder()

    # 1. Головна кнопка Кошика (на всю ширину)
    builder.row(InlineKeyboardButton(
        text=f'🧺 Кошик: {total_price if total_price else 0} UAH', 
        callback_data='Ваш кошик'
    ))

    # 2. НОВА КНОПКА: Ексклюзиви (на всю ширину під кошиком)
    # Ми прив'язуємо її до ID 15, де будуть твої нові страви
    builder.row(InlineKeyboardButton(
        text='🔥 Товари тижня & Ексклюзиви', 
        callback_data='category_15' 
    ))

    # Розподіляємо решту категорій (крім 15-ї, бо вона вже зверху)
    main_buttons = []
    end_buttons = []

    for cat in categories:
        if cat.id == 15: # Пропускаємо, бо ми вже додали її вручну вище
            continue
            
        name_low = cat.category_name.lower()
        btn = InlineKeyboardButton(text=cat.category_name, callback_data=f'category_{cat.id}')
        
        # Ховаємо технічні категорії в кінець
        if any(x in name_low for x in ["соуси", "закуски", "добавки"]):
            end_buttons.append(btn)
        else:
            main_buttons.append(btn)

    # 3. Виводимо Основні страви (по 2 в ряд)
    builder.add(*main_buttons)

    # 4. Виводимо Соуси/Закуски в самому кінці
    builder.add(*end_buttons)

    # Налаштовуємо сітку: Кошик(1), Ексклюзиви(1), решта по (2)
    builder.adjust(1, 1, 2)

    return builder.as_markup()
    

def show_product_by_category(category_id: int) -> InlineKeyboardMarkup:
    products = db_get_products(category_id)
    builder = InlineKeyboardBuilder()
    [builder.button(text=product.product_name,
                    callback_data=f"product_{product.id}") for product in products]
    builder.adjust(2)
    builder.row(
        InlineKeyboardButton(text='🔙 Назад ', callback_data='return_to_category')
    )

    return builder.as_markup()

# Додай category_id як аргумент, щоб кнопка знала куди повертатись
def generate_constructor_button(quantity: int = 1, category_id: int = None) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    # Кнопки + / - / Кількість
    builder.button(text='➖', callback_data='prod_minus')
    builder.button(text=str(quantity), callback_data='ignore')
    builder.button(text='➕', callback_data='prod_plus')
    
    builder.button(text='Покласти в кошик 🧺', callback_data='put_into_cart')
    
    # ТУТ МАГІЯ: передаємо ID категорії в колбек кнопки Назад
    callback_back = f"back_to_list_{category_id}" if category_id else "return_to_category"
    builder.button(text='🔙 Назад', callback_data=callback_back)

    builder.adjust(3, 1, 1)
    return builder.as_markup()


def generate_delete_product(chat_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    cart_products = db_get_product_for_delete(chat_id)  # теперь должна возвращать id, name, quantity

    for finally_cart_id, product_name, quantity in cart_products:
        # Кнопки уменьшить/плюс/удалить
        builder.button(text='➖', callback_data=f'change_{finally_cart_id}_minus')
        builder.button(text=str(quantity), callback_data=f'quantity_{finally_cart_id}')
        builder.button(text='➕', callback_data=f'change_{finally_cart_id}_plus')
        builder.button(text='❌', callback_data=f'delete_{finally_cart_id}')

    # Кнопка оформить заказ
    builder.button(text='🚀 Оформити замовлення', callback_data='order_pay')

    builder.adjust(4)  # 4 кнопки на ряд
    return builder.as_markup()