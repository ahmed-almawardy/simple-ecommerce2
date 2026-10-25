from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from ..database import get_db
from ..deps import get_current_user
from ..models import CartItem, Product, User, utcnow
from ..schemas import CartAddIn, CartItemOut, CartOut, CartUpdateIn

router = APIRouter(prefix="/api/cart", tags=["cart"])


def build_cart(db: Session, user: User) -> CartOut:
    rows = db.scalars(
        select(CartItem)
        .options(joinedload(CartItem.product).joinedload(Product.category))
        .where(CartItem.user_id == user.id)
        .order_by(CartItem.id)
    ).all()
    items = [
        CartItemOut(product=r.product, quantity=r.quantity, line_total_cents=r.product.price_cents * r.quantity)
        for r in rows
    ]
    return CartOut(items=items, total_cents=sum(i.line_total_cents for i in items), count=sum(i.quantity for i in items))


def _touch(user: User) -> None:
    # cart changed -> a new abandoned-cart reminder may be sent later
    user.cart_reminder_sent_at = None


@router.get("", response_model=CartOut)
def get_cart(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return build_cart(db, user)


@router.post("/items", response_model=CartOut)
def add_item(data: CartAddIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    product = db.get(Product, data.product_id)
    if not product:
        raise HTTPException(404, "Product not found")
    item = db.scalar(select(CartItem).where(CartItem.user_id == user.id, CartItem.product_id == product.id))
    new_qty = (item.quantity if item else 0) + data.quantity
    if new_qty > product.stock:
        raise HTTPException(400, f"Only {product.stock} left in stock")
    if item:
        item.quantity = new_qty
        item.updated_at = utcnow()
    else:
        db.add(CartItem(user_id=user.id, product_id=product.id, quantity=new_qty))
    _touch(user)
    db.add(user)
    db.commit()
    return build_cart(db, user)


@router.patch("/items/{product_id}", response_model=CartOut)
def update_item(product_id: int, data: CartUpdateIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    item = db.scalar(select(CartItem).where(CartItem.user_id == user.id, CartItem.product_id == product_id))
    if not item:
        raise HTTPException(404, "Item not in cart")
    if data.quantity == 0:
        db.delete(item)
    else:
        if data.quantity > item.product.stock:
            raise HTTPException(400, f"Only {item.product.stock} left in stock")
        item.quantity = data.quantity
        item.updated_at = utcnow()
    _touch(user)
    db.add(user)
    db.commit()
    return build_cart(db, user)


@router.delete("/items/{product_id}", response_model=CartOut)
def remove_item(product_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    item = db.scalar(select(CartItem).where(CartItem.user_id == user.id, CartItem.product_id == product_id))
    if item:
        db.delete(item)
        _touch(user)
        db.add(user)
        db.commit()
    return build_cart(db, user)
