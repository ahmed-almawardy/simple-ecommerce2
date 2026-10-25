from contextlib import asynccontextmanager

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import Base, engine
from .reminders import send_abandoned_cart_reminders
from .routers import auth, cart, orders, products
from .seed import seed


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)  # use Alembic for real migrations in production
    seed()
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        send_abandoned_cart_reminders, "interval", minutes=settings.REMINDER_CHECK_INTERVAL_MINUTES, id="cart-reminders"
    )
    scheduler.start()
    yield
    scheduler.shutdown(wait=False)


app = FastAPI(title=f"{settings.BRAND} Store API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.CORS_ORIGINS.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for r in (auth.router, products.router, cart.router, orders.router):
    app.include_router(r)


@app.get("/api/health")
def health():
    return {"status": "ok"}
