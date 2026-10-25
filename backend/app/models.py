from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(120))
    hashed_password: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    # set when a reminder was sent; reset to None whenever the cart changes
    cart_reminder_sent_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    cart_items: Mapped[list["CartItem"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Category(Base):
    __tablename__ = "categories"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80))
    slug: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    image_url: Mapped[str] = mapped_column(String(500), default="")


class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), index=True)
    slug: Mapped[str] = mapped_column(String(220), unique=True, index=True)
    description: Mapped[str] = mapped_column(Text, default="")
    price_cents: Mapped[int] = mapped_column(Integer)
    image_url: Mapped[str] = mapped_column(String(500))
    images: Mapped[list] = mapped_column(JSON, default=list)
    stock: Mapped[int] = mapped_column(Integer, default=0)
    brand: Mapped[str] = mapped_column(String(80), default="")
    energy_rating: Mapped[str] = mapped_column(String(2), default="")  # A..G, empty = not applicable
    warranty_months: Mapped[int] = mapped_column(Integer, default=24)
    specs: Mapped[dict] = mapped_column(JSON, default=dict)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    category: Mapped[Category] = relationship()


class CartItem(Base):
    __tablename__ = "cart_items"
    __table_args__ = (UniqueConstraint("user_id", "product_id"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow)

    user: Mapped[User] = relationship(back_populates="cart_items")
    product: Mapped[Product] = relationship()


class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending | paid
    total_cents: Mapped[int] = mapped_column(Integer)
    stripe_session_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    full_name: Mapped[str] = mapped_column(String(120))
    address: Mapped[str] = mapped_column(String(255))
    city: Mapped[str] = mapped_column(String(120))
    postal_code: Mapped[str] = mapped_column(String(20))
    country: Mapped[str] = mapped_column(String(80))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    user: Mapped[User] = relationship()
    items: Mapped[list["OrderItem"]] = relationship(back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    name: Mapped[str] = mapped_column(String(200))
    image_url: Mapped[str] = mapped_column(String(500), default="")
    unit_price_cents: Mapped[int] = mapped_column(Integer)
    quantity: Mapped[int] = mapped_column(Integer)

    order: Mapped[Order] = relationship(back_populates="items")
