from pathlib import Path
from aiogram import Router, F, types
from aiogram.types import Message, CallbackQuery, FSInputFile

from config import MEDIA_PATH
from telegramBotCafe.database.db_utils import (
    db_get_product_by_id, 
    db_get_product_by_name, 
    db_get_user_cart, 
    db_add_to_finally_cart,
    db_get_all_category,
    db_get_finally_price,
    db_get_products
)
from telegramBotCafe.keyboards.inline_kb import (
    show_product_by_category, 
    generate_constructor_button, 
    generate_category_menu
)
from telegramBotCafe.keyboards.reply_kb import back_to_main_menu, share_phone_button
from telegramBotCafe.utils.caption import text_for_caption


router = Router()


def get_image_path(image_name):
    return Path(MEDIA_PATH) / image_name



@router.message(F.text == "✅ Зробити замовлення")
async def make_order(message: Message):
    chat_id = message.from_user.id
    await message.answer("🪄 Розпочнемо", reply_markup=back_to_main_menu())

    categories = await db_get_all_category()
    total_price = await db_get_finally_price(chat_id)

    await message.answer(
        text="🥡 Виберіть категорію", 
        reply_markup=generate_category_menu(categories, total_price)
    )


@router.callback_query(F.data.startswith("category_"))
async def show_product_button(call: CallbackQuery):
    category_id = int(call.data.split("_")[-1])

    products = await db_get_products(category_id)

    await call.message.edit_text(
        text="🥢 Виберіть продукт",
        reply_markup=show_product_by_category(products),
    )
    await call.answer()


@router.callback_query(F.data.startswith("product_"))
async def show_product_detail(call: CallbackQuery):
    product_id = int(call.data.split("_")[-1])
    product = await db_get_product_by_id(product_id)
    
    if not product:
        return await call.answer("❌ Товар не знайдено!")

    user_cart = await db_get_user_cart(call.from_user.id)

    if user_cart:
        image_path = get_image_path(product.image.strip())
        text = text_for_caption(
            name=product.product_name,
            description=product.description,
            price=product.price,
            dish_weight=product.dish_weight,
        )
        await call.message.delete()
        await call.message.answer_photo(
            photo=FSInputFile(str(image_path)),
            caption=text,
            reply_markup=generate_constructor_button(
                quantity=1, 
                category_id=product.category_id
            ),
        )
    else:
        await call.message.answer(
            text="😿 На жаль, у нас немає Вашого контакту",
            reply_markup=share_phone_button(),
        )
    await call.answer()


@router.callback_query(F.data.in_(["prod_plus", "prod_minus"]))
async def constructor_change(call: CallbackQuery):

    product_name = call.message.caption.split("\n")[0].strip()
    product = await db_get_product_by_name(product_name)

    if not product:
        return await call.answer("❌ Товар не знайдено")

    current_qty = int(call.message.reply_markup.inline_keyboard[0][1].text)

    if call.data == "prod_plus":
        new_qty = current_qty + 1
    else:
        if current_qty <= 1:
            return await call.answer("❗️ Менше одного вибрати не можна")
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
            quantity=new_qty, 
            category_id=product.category_id
        ),
        parse_mode="HTML",
    )
    await call.answer()


@router.callback_query(F.data == "put_into_cart")
async def put_into_cart_handler(call: CallbackQuery):
    chat_id = call.from_user.id 
    quantity = int(call.message.reply_markup.inline_keyboard[0][1].text)
    product_name = call.message.caption.split("\n")[0].strip()

    product = await db_get_product_by_name(product_name)
    user_cart = await db_get_user_cart(chat_id)

    if product and user_cart:
        await db_add_to_finally_cart(
            cart_id=user_cart.id,
            product_name=product.product_name,
            price=product.price,
            quantity=quantity,
        )

        categories = await db_get_all_category()
        total_price = await db_get_finally_price(chat_id)

        await call.answer(f"✅ {product_name} додано!")
        await call.message.delete()
        await call.message.answer(
            text="✅ Товар додано! Виберіть наступну категорію:",
            reply_markup=generate_category_menu(categories, total_price),
        )
    else:
        await call.answer("❌ Помилка додавання", show_alert=True)


@router.callback_query(F.data == "return_to_category")
async def back_to_categories_menu(call: CallbackQuery):
    chat_id = call.from_user.id
    
    categories = await db_get_all_category()
    total_price = await db_get_finally_price(chat_id)

    await call.message.delete()
    await call.message.answer(
        text="<b>🥡 Оберіть категорію:</b>",
        reply_markup=generate_category_menu(categories, total_price),
        parse_mode="HTML",
    )
    await call.answer()


@router.callback_query(F.data.startswith("back_to_list_"))
async def back_to_products_list(call: CallbackQuery):
    category_id = int(call.data.split("_")[-1])

    products = await db_get_products(category_id)
    
    await call.message.delete()
    await call.message.answer(
        text="🥢 Виберіть продукт",
        reply_markup=show_product_by_category(products),
    )
    await call.answer()


