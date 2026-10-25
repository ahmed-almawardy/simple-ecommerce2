"""Checkout + payments.

Real payments use Stripe Checkout (hosted page). When STRIPE_SECRET_KEY is empty a
built-in MOCK payment page is used instead so the full flow can be tested locally.
"""
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from sqlalchemy import delete, select
from sqlalchemy.orm import Session, joinedload

from ..config import settings
from ..database import get_db
from ..deps import get_current_user
from ..emails import send_payment_success_email
from ..models import CartItem, Order, OrderItem, Product, User, utcnow
from ..schemas import CheckoutIn, CheckoutOut, ConfirmIn, OrderOut

router = APIRouter(prefix="/api", tags=["orders"])

try:
    import stripe
except ImportError:  # pragma: no cover
    stripe = None


def stripe_enabled() -> bool:
    return bool(settings.STRIPE_SECRET_KEY and stripe)


def finalize_order(db: Session, order: Order) -> bool:
    """Mark paid, decrement stock, clear cart. Idempotent. Returns True only the first time."""
    if order.status == "paid":
        return False
    order.status = "paid"
    order.paid_at = utcnow()
    for it in order.items:
        product = db.get(Product, it.product_id)
        if product:
            product.stock = max(0, product.stock - it.quantity)
    db.execute(delete(CartItem).where(CartItem.user_id == order.user_id))
    db.commit()
    return True


def queue_receipt(background: BackgroundTasks, order: Order) -> None:
    items = [(i.name, i.quantity, i.unit_price_cents) for i in order.items]
    background.add_task(
        send_payment_success_email, order.user.email, order.user.full_name, order.id, items, order.total_cents
    )


def _load_order(db: Session, order_id: int) -> Order | None:
    return db.scalar(select(Order).options(joinedload(Order.items), joinedload(Order.user)).where(Order.id == order_id))


@router.post("/orders/checkout", response_model=CheckoutOut)
def checkout(data: CheckoutIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    cart = db.scalars(select(CartItem).options(joinedload(CartItem.product)).where(CartItem.user_id == user.id)).all()
    if not cart:
        raise HTTPException(400, "Your cart is empty")
    for c in cart:
        if c.quantity > c.product.stock:
            raise HTTPException(400, f"'{c.product.name}' only has {c.product.stock} left in stock")

    order = Order(
        user_id=user.id,
        total_cents=sum(c.product.price_cents * c.quantity for c in cart),
        **data.model_dump(),
    )
    order.items = [
        OrderItem(
            product_id=c.product_id,
            name=c.product.name,
            image_url=c.product.image_url,
            unit_price_cents=c.product.price_cents,
            quantity=c.quantity,
        )
        for c in cart
    ]
    db.add(order)
    db.commit()

    if not stripe_enabled():
        return CheckoutOut(order_id=order.id, payment_url=f"{settings.FRONTEND_URL}/checkout/mock?order_id={order.id}")

    stripe.api_key = settings.STRIPE_SECRET_KEY
    session = stripe.checkout.Session.create(
        mode="payment",
        customer_email=user.email,
        client_reference_id=str(order.id),
        metadata={"order_id": str(order.id)},
        line_items=[
            {
                "quantity": i.quantity,
                "price_data": {
                    "currency": settings.CURRENCY,
                    "unit_amount": i.unit_price_cents,
                    "product_data": {"name": i.name},
                },
            }
            for i in order.items
        ],
        success_url=f"{settings.FRONTEND_URL}/checkout/success?order_id={order.id}&session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{settings.FRONTEND_URL}/cart",
    )
    order.stripe_session_id = session.id
    db.commit()
    return CheckoutOut(order_id=order.id, payment_url=session.url)


@router.post("/orders/confirm", response_model=OrderOut)
def confirm(data: ConfirmIn, background: BackgroundTasks, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Called by the success page; verifies the session with Stripe (works even if the webhook is late)."""
    order = db.scalar(
        select(Order).options(joinedload(Order.items), joinedload(Order.user)).where(
            Order.stripe_session_id == data.session_id, Order.user_id == user.id
        )
    )
    if not order:
        raise HTTPException(404, "Order not found")
    if order.status != "paid" and stripe_enabled():
        stripe.api_key = settings.STRIPE_SECRET_KEY
        session = stripe.checkout.Session.retrieve(data.session_id)
        if session.payment_status == "paid" and finalize_order(db, order):
            queue_receipt(background, order)
    return order


@router.post("/orders/{order_id}/mock-pay", response_model=OrderOut)
def mock_pay(order_id: int, background: BackgroundTasks, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if stripe_enabled():
        raise HTTPException(404, "Not found")
    order = _load_order(db, order_id)
    if not order or order.user_id != user.id:
        raise HTTPException(404, "Order not found")
    if finalize_order(db, order):
        queue_receipt(background, order)
    return order


@router.post("/stripe/webhook")
async def stripe_webhook(request: Request, background: BackgroundTasks, db: Session = Depends(get_db)):
    if not stripe_enabled():
        raise HTTPException(404, "Stripe not configured")
    payload = await request.body()
    try:
        event = stripe.Webhook.construct_event(
            payload, request.headers.get("stripe-signature", ""), settings.STRIPE_WEBHOOK_SECRET
        )
    except Exception:
        raise HTTPException(400, "Invalid signature")
    if event["type"] == "checkout.session.completed":
        obj = event["data"]["object"]
        order = _load_order(db, int(obj["metadata"]["order_id"]))
        if order and obj.get("payment_status") == "paid" and finalize_order(db, order):
            queue_receipt(background, order)
    return {"received": True}


@router.get("/orders", response_model=list[OrderOut])
def my_orders(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.scalars(
        select(Order).options(joinedload(Order.items)).where(Order.user_id == user.id).order_by(Order.id.desc())
    ).unique().all()


@router.get("/orders/{order_id}", response_model=OrderOut)
def get_order(order_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    order = _load_order(db, order_id)
    if not order or order.user_id != user.id:
        raise HTTPException(404, "Order not found")
    return order
