from typing import Iterable
from functools import wraps
from sqlalchemy import update, delete, select, func
from sqlalchemy.exc import IntegrityError
from database.engine import connection

from database.engine import AsyncSessionLocal
from database.models import Users, Categories, Carts, FinallyCarts, Products


@connection
async def db_register_user(session, full_name: str, chat_id: int) -> bool:
    try:
        user = Users(name=full_name, telegram=chat_id)
        session.add(user)
        await session.commit()
        return False
    except IntegrityError:
        return True

@connection
async def db_update_user(session, chat_id: int, phone: str):
    await session.execute(
        update(Users).where(Users.telegram == chat_id).values(phone=phone)
    )
    await session.commit()

@connection
async def db_get_user_info(session, chat_id: int) -> Users:
    return await session.scalar(select(Users).where(Users.telegram == chat_id))


@connection
async def db_get_all_category(session) -> Iterable:
    result = await session.execute(select(Categories))
    return result.scalars().all()

@connection
async def db_get_products(session, category_id: int) -> Iterable:
    result = await session.execute(select(Products).where(Products.category_id == category_id))
    return result.scalars().all()

@connection
async def db_get_product_by_id(session, product_id: int) -> Products:
    return await session.get(Products, product_id)

@connection
async def db_get_product_by_name(session, product_name: str) -> Products | None:
    return await session.scalar(select(Products).where(Products.product_name == product_name))


@connection
async def db_create_user_cart(session, chat_id: int):
    try:
        user = await session.scalar(select(Users).where(Users.telegram == chat_id))
        if user:
            session.add(Carts(user_id=user.id))
            await session.commit()
            return True
    except (IntegrityError, AttributeError):
        return False

@connection
async def db_get_user_cart(session, chat_id: int) -> Carts | None:
    query = select(Carts).join(Users).where(Users.telegram == chat_id)
    return await session.scalar(query)

@connection
async def db_add_to_finally_cart(session, cart_id, product_name, price, quantity):
    item = await session.scalar(
        select(FinallyCarts).filter_by(cart_id=cart_id, product_name=product_name)
    )
    if item:
        item.quantity += quantity
        item.final_price = float(price) * item.quantity
    else:
        session.add(FinallyCarts(
            cart_id=cart_id, product_name=product_name,
            quantity=quantity, final_price=float(price) * quantity
        ))
    await session.commit()

@connection
async def db_get_finally_price(session, chat_id: int):
    query = select(func.sum(FinallyCarts.final_price)).join(Carts).join(Users).where(Users.telegram == chat_id)
    result = await session.execute(query)
    total = result.scalar()
    return total if total else 0

@connection
async def db_get_finally_cart_products(session, chat_id: int):
    query = select(FinallyCarts).join(Carts).join(Users).where(Users.telegram == chat_id).order_by(FinallyCarts.id.asc())
    result = await session.execute(query)
    return result.scalars().all()

@connection
async def db_delete_product(session, finally_id: int):
    await session.execute(delete(FinallyCarts).where(FinallyCarts.id == finally_id))
    await session.commit()

@connection
async def db_update_quantity(session, finally_id: int, delta: int):
    item = await session.get(FinallyCarts, finally_id)
    if item:
        new_qty = max(1, item.quantity + delta)
        if new_qty != item.quantity:
            unit_price = float(item.final_price) / item.quantity
            item.quantity = new_qty
            item.final_price = unit_price * new_qty
            await session.commit()

@connection
async def clear_finally_cart(session, user_telegram_id: int):
    cart = await session.scalar(select(Carts).join(Users).where(Users.telegram == user_telegram_id))
    if cart:
        await session.execute(delete(FinallyCarts).where(FinallyCarts.cart_id == cart.id))
        await session.commit()