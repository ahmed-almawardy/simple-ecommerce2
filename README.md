# VOLTA – Home electronics & appliances store (FastAPI + Nuxt 3)

A complete store for home electronics and appliances (kitchen, laundry, cooling & heating, cleaning, TV & audio, smart home): landing page, categories + filters (brand, price, energy rating), product pages with spec sheet and warranty, cart, checkout, Stripe payment,
registration/login, and three transactional emails (welcome, payment receipt, abandoned-cart reminder).

```
shop/
├── backend/    FastAPI + SQLAlchemy (SQLite by default, Postgres ready)
├── frontend/   Nuxt 3 (Vue 3)
└── docker-compose.yml   optional: Mailhog (email inbox) + Postgres
```

## Run it (3 terminals)

```bash
# 1) optional email inbox -> http://localhost:8025
docker compose up mailhog -d

# 2) backend  -> http://localhost:8000/docs
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload

# 3) frontend -> http://localhost:3000
cd frontend
npm install
npm run dev
```

The database is created and seeded with 26 demo appliances (fictional brands, with specs, energy ratings and warranty) on first start.
Without Mailhog, set `SMTP_HOST=` (empty) in `backend/.env` and emails are printed in the backend console.

## Features → where they live

| Feature | Backend | Frontend |
|---|---|---|
| Landing page, categories | `routers/products.py` | `pages/index.vue` |
| Category, brand, energy rating, price, stock filters, search, sort, pagination | `GET /api/products`, `/api/facets` | `pages/products/index.vue` (state in URL query) |
| Product page (photos, description, add to cart) | `GET /api/products/{slug}` | `pages/products/[slug].vue` |
| Registration + login (JWT, bcrypt) | `routers/auth.py` | `pages/login.vue`, `register.vue` |
| Cart (saved on the server per user) | `routers/cart.py` | `pages/cart.vue` |
| Checkout + payment | `routers/orders.py` | `pages/checkout/*` |
| Welcome email | `emails.send_welcome_email` (on register) | |
| Payment success email | `emails.send_payment_success_email` (on paid) | |
| Abandoned-cart reminder | `reminders.py` (scheduler in `main.py`) | |

## Payments

* **No keys (default):** checkout redirects to a built-in demo payment page (`/checkout/mock`) with a
  "simulate successful payment" button. Great for development, never use in production.
* **Stripe:** set in `backend/.env`
  ```
  STRIPE_SECRET_KEY=sk_test_...
  STRIPE_WEBHOOK_SECRET=whsec_...
  ```
  Checkout creates a Stripe Checkout Session and redirects the shopper to Stripe's hosted page.
  An order is marked **paid** (stock decremented, cart cleared, receipt emailed) either by the webhook
  `POST /api/stripe/webhook` or by the success page calling `POST /api/orders/confirm` – whichever comes first;
  the operation is idempotent, so the email is sent only once. For local webhooks:
  `stripe listen --forward-to localhost:8000/api/stripe/webhook`. Test card: `4242 4242 4242 4242`.

## Abandoned-cart reminder

A background job runs every `REMINDER_CHECK_INTERVAL_MINUTES` (default 5). If a user's cart has had no change for
`ABANDONED_CART_MINUTES` (default 60) and no reminder was sent for that cart state, one email is sent.
Any cart change re-arms it; paying clears the cart. To test quickly set `ABANDONED_CART_MINUTES=1` and
`REMINDER_CHECK_INTERVAL_MINUTES=1`, add something to the cart, wait ~2 minutes, check Mailhog.

If you run several backend workers/instances, run the scheduler in only one (or move it to a worker such as Celery/cron).

## Tests

```bash
cd backend && pytest -q
```
Covers catalog filters, register/login, cart, reminder (sent once), mock checkout, receipt email, stock update, idempotency.

## Before going to production

* Set a strong `JWT_SECRET`, real `FRONTEND_URL`/`CORS_ORIGINS`, real SMTP (SendGrid, SES, Postmark…) and Stripe live keys.
* Replace the demo `picsum.photos` images with your own (`image_url` / `images` on each product; add an admin or upload flow).
* Use Postgres + Alembic migrations (the app uses `create_all` for convenience).
* Add rate limiting on auth endpoints, email verification / password reset, and an admin panel for products & orders.
* "VOLTA" is a placeholder brand – change `BRAND` in `backend/.env` and the logo/colors in `frontend/`.
* Edit the catalog in `backend/app/seed.py` (categories, products, specs, energy rating, warranty). Delete `backend/shop.db` to re-seed.
* Product fields: `energy_rating` (A–G, empty if n/a), `warranty_months`, `specs` (key/value table shown on the product page).
