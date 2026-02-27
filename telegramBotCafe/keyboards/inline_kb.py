from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup, InlineKeyboardButton


def generate_category_menu(categories, total_price: float = 0) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(
        text=f'🧺 Кошик: {total_price if total_price else 0} UAH', 
        callback_data='Ваш кошик'
    ))

    builder.row(InlineKeyboardButton(
        text='🔥 Товари тижня & Ексклюзиви', 
        callback_data='category_15' 
    ))

    main_buttons = []
    end_buttons = []

    for cat in categories:
        if cat.id == 15:
            continue
            
        name_low = cat.category_name.lower()
        btn = InlineKeyboardButton(text=cat.category_name, callback_data=f'category_{cat.id}')
        
        if any(x in name_low for x in ["соуси", "закуски", "добавки"]):
            end_buttons.append(btn)
        else:
            main_buttons.append(btn)

    builder.add(*main_buttons)
    builder.add(*end_buttons)

    builder.adjust(1, 1, 2)
    return builder.as_markup()


def show_product_by_category(products) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for product in products:
        builder.button(text=product.product_name, callback_data=f"product_{product.id}")
    
    builder.adjust(2)
    builder.row(
        InlineKeyboardButton(text='🔙 Назад ', callback_data='return_to_category')
    )
    return builder.as_markup()


def generate_constructor_button(quantity: int = 1, category_id: int = None) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    builder.button(text='➖', callback_data='prod_minus')
    builder.button(text=str(quantity), callback_data='ignore')
    builder.button(text='➕', callback_data='prod_plus')
    
    builder.button(text='Покласти в кошик 🧺', callback_data='put_into_cart')
    
    callback_back = f"back_to_list_{category_id}" if category_id else "return_to_category"
    builder.button(text='🔙 Назад', callback_data=callback_back)

    builder.adjust(3, 1, 1)
    return builder.as_markup()


def generate_cart_keyboard(cart_products) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    for p in cart_products:
        builder.row(InlineKeyboardButton(text=f"🔹 {p.product_name}", callback_data="ignore"))
        builder.row(
            InlineKeyboardButton(text="➖", callback_data=f"decrease_{p.id}"),
            InlineKeyboardButton(text=f"{p.quantity} шт.", callback_data="ignore"),
            InlineKeyboardButton(text="➕", callback_data=f"increase_{p.id}"),
            InlineKeyboardButton(text="❌", callback_data=f"delete_{p.id}"),
        )
    
    builder.row(InlineKeyboardButton(text="🚀 Оформити замовлення", callback_data="order_pay"))
    builder.row(InlineKeyboardButton(text="🔙 Повернутися в меню", callback_data="return_to_category"))
    
    return builder.as_markup()