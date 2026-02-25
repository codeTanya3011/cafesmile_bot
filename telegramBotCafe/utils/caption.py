from database.db_utils import db_get_finally_cart_products


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
    

def counting_products_from_cart(chat_id, user_text):
    products = db_get_finally_cart_products(chat_id)
    if products:
        text = f'{user_text}\n\n'
        total_products = total_price = count = 0
        for name, quantity, price, cart_id in products:
            count += 1
            total_products += quantity
            total_price += price
            text += f'{count}. {name}\nКількість: {quantity}\nВартість: {price}\n\n'

        text += f'Загальна кількість продуктів: {total_products}\nЗагальна вартість кошика: {total_price}'

        context = (count, text, total_price, chat_id)
        return context




