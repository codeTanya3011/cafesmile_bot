from sqlalchemy import String, BigInteger, DECIMAL, ForeignKey, UniqueConstraint, Text, Float, DateTime, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from datetime import datetime

from telegramBotCafe.database.base import Base


class Users(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    telegram: Mapped[int] = mapped_column(BigInteger, unique=True)
    phone: Mapped[str | None] = mapped_column(String(15), nullable=True)

    carts: Mapped[list["Carts"]] = relationship(
        back_populates='user_cart', 
        cascade="all, delete-orphan"
    )
    orders: Mapped[list["Orders"]] = relationship(back_populates="user")

    def __str__(self):
        return self.name


class Categories(Base):
    __tablename__ = 'categories'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    category_name: Mapped[str] = mapped_column(String(100))

    products: Mapped[list["Products"]] = relationship(
        back_populates='product_category',
        lazy='select'
    )

    def __str__(self):
        return self.category_name


class Products(Base):
    __tablename__ = 'products'

    id: Mapped[int] = mapped_column(primary_key=True)
    product_name: Mapped[str] = mapped_column(String(100), unique=True)
    description: Mapped[str] = mapped_column()
    image: Mapped[str] = mapped_column(String(100))
    price: Mapped[float] = mapped_column(DECIMAL(12, 2))
    category_id: Mapped[int] = mapped_column(ForeignKey('categories.id'))
    dish_weight: Mapped[int | None] = mapped_column(nullable=True)

    product_category: Mapped["Categories"] = relationship(back_populates='products')


class Carts(Base):
    __tablename__ = 'carts'

    id: Mapped[int] = mapped_column(primary_key=True)
    total_price: Mapped[float] = mapped_column(DECIMAL(12, 2), default=0)
    total_products: Mapped[int] = mapped_column(default=0)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), unique=True)

    user_cart: Mapped["Users"] = relationship(back_populates='carts')
    finally_id: Mapped[list["FinallyCarts"]] = relationship(
        back_populates='user_cart', 
        cascade="all, delete-orphan"
    )

    def __str__(self):
        return f"Cart {self.id}"


class FinallyCarts(Base):
    __tablename__ = 'finally_carts'

    id: Mapped[int] = mapped_column(primary_key=True)
    product_name: Mapped[str] = mapped_column(String(100))
    final_price: Mapped[float] = mapped_column(DECIMAL(12, 2))
    quantity: Mapped[int] = mapped_column()
    cart_id: Mapped[int] = mapped_column(ForeignKey('carts.id'))

    user_cart: Mapped["Carts"] = relationship(back_populates='finally_id')

    __table_args__ = (UniqueConstraint('cart_id', 'product_name'),)


class Orders(Base):
    __tablename__ = 'orders'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.telegram'))
    order_content: Mapped[str] = mapped_column(Text)
    total_amount: Mapped[float] = mapped_column(Float)
    delivery_type: Mapped[str] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    user: Mapped["Users"] = relationship(back_populates="orders")