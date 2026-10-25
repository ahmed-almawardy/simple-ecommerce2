import os

os.environ["DATABASE_URL"] = "sqlite:///./test_shop.db"
os.environ["SMTP_HOST"] = ""
os.environ["STRIPE_SECRET_KEY"] = ""
os.environ["ABANDONED_CART_MINUTES"] = "0"

from datetime import timedelta  # noqa: E402

from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import select  # noqa: E402

from app.database import SessionLocal  # noqa: E402
from app.main import app  # noqa: E402
from app.models import CartItem, utcnow  # noqa: E402
from app.reminders import send_abandoned_cart_reminders  # noqa: E402


def test_full_flow(capsys):
    with TestClient(app) as c:
        # catalog + filters
        assert len(c.get("/api/categories").json()) == 6
        r = c.get("/api/products", params={"category": "kitchen", "max_price": 200, "sort": "price_asc"}).json()
        assert r["total"] > 0 and all(p["price_cents"] <= 20000 for p in r["items"])
        f = c.get("/api/facets").json()
        assert f["brands"] and "A" in f["energy_ratings"]
        assert c.get("/api/products", params={"energy": ["A"]}).json()["total"] > 0
        slug = r["items"][0]["slug"]
        product = c.get(f"/api/products/{slug}").json()
        assert product["specs"] and product["warranty_months"] > 0

        # register (+ welcome email) and login
        reg = c.post("/api/auth/register", json={"full_name": "Jane Doe", "email": "jane@example.com", "password": "password123"})
        assert reg.status_code == 201
        assert "Welcome to" in capsys.readouterr().out
        assert c.post("/api/auth/register", json={"full_name": "J", "email": "jane@example.com", "password": "password123"}).status_code in (409, 422)
        assert c.post("/api/auth/login", json={"email": "jane@example.com", "password": "bad"}).status_code == 401
        token = c.post("/api/auth/login", json={"email": "jane@example.com", "password": "password123"}).json()["access_token"]
        h = {"Authorization": f"Bearer {token}"}

        # cart
        assert c.get("/api/cart").status_code == 401
        cart = c.post("/api/cart/items", headers=h, json={"product_id": product["id"], "quantity": 2}).json()
        assert cart["count"] == 2 and cart["total_cents"] == product["price_cents"] * 2

        # abandoned cart reminder (idle time is 0 in this test) - sent once only
        with SessionLocal() as db:
            for ci in db.scalars(select(CartItem)).all():
                ci.updated_at = utcnow() - timedelta(minutes=5)
            db.commit()
        assert send_abandoned_cart_reminders() == 1
        assert "Your cart is waiting" in capsys.readouterr().out
        assert send_abandoned_cart_reminders() == 0

        # checkout (mock payment) + receipt email + stock + cart cleared
        co = c.post("/api/orders/checkout", headers=h, json={"full_name": "Jane Doe", "address": "1 Main St", "city": "NYC", "postal_code": "10001", "country": "US"}).json()
        assert "/checkout/mock" in co["payment_url"]
        paid = c.post(f"/api/orders/{co['order_id']}/mock-pay", headers=h).json()
        assert paid["status"] == "paid"
        assert "Payment received" in capsys.readouterr().out
        assert c.get("/api/cart", headers=h).json()["count"] == 0
        assert c.get(f"/api/products/{slug}").json()["stock"] == product["stock"] - 2
        assert len(c.get("/api/orders", headers=h).json()) == 1
        # idempotent: second call sends no second email
        c.post(f"/api/orders/{co['order_id']}/mock-pay", headers=h)
        assert "Payment received" not in capsys.readouterr().out
