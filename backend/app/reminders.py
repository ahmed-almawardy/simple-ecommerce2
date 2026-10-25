"""Abandoned-cart reminders.

A user gets ONE reminder per "cart state": when the newest item in their cart has been idle for
ABANDONED_CART_MINUTES and no reminder was sent yet. Any cart change resets the flag.
"""
from datetime import timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import joinedload

from .config import settings
from .database import SessionLocal
from .emails import send_abandoned_cart_email
from .models import CartItem, Product, User, utcnow


def send_abandoned_cart_reminders() -> int:
    cutoff = utcnow() - timedelta(minutes=settings.ABANDONED_CART_MINUTES)
    sent = 0
    with SessionLocal() as db:
        last_touch = (
            select(CartItem.user_id, func.max(CartItem.updated_at).label("last"))
            .group_by(CartItem.user_id)
            .subquery()
        )
        users = db.scalars(
            select(User)
            .join(last_touch, last_touch.c.user_id == User.id)
            .where(last_touch.c.last <= cutoff, User.cart_reminder_sent_at.is_(None))
        ).all()
        for user in users:
            rows = db.scalars(
                select(CartItem).options(joinedload(CartItem.product)).where(CartItem.user_id == user.id)
            ).all()
            if not rows:
                continue
            items = [(r.product.name, r.quantity, r.product.price_cents) for r in rows]
            total = sum(q * p for _, q, p in items)
            send_abandoned_cart_email(user.email, user.full_name, items, total)
            user.cart_reminder_sent_at = utcnow()
            sent += 1
        db.commit()
    return sent
