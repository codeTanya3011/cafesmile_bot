from telegramBotCafe.database.db_utils import db_get_finally_cart_products


def text_for_caption(name, description, price, dish_weight, quantity=1):
    total = float(price) * quantity
    return (
        f"<b>{name}</b>\n\n"
        f"Інгредієнти: {description}\n\n"
        f"Вага: {dish_weight} г/мл\n\n"
        f"<b>Ціна:</b> {price} UAH\n"
        f"───────────────────\n"
        f"<b>СУМА: {total} UAH</b>"
    )


async def counting_products_from_cart(chat_id, user_text, products):
    if products:
        text = f'<b>{user_text}</b>\n\n'
        total_products = 0
        total_price = 0
        count = 0
        
        for p in products:
            count += 1
            total_products += p.quantity
            total_price += float(p.final_price) 
            
            text += (f'{count}. <b>{p.product_name}</b>\n'
                     f'Кількість: {p.quantity} шт.\n'
                     f'Вартість: {p.final_price} UAH\n\n')

        text += "───────────────────\n"
        text += f'Загальна кількість товарів: {total_products}\n'
        text += f'<b>Загальна вартість кошика: {total_price} UAH</b>'

        return count, text, total_price, chat_id
    
    return 0, "Кошик порожній", 0, chat_id