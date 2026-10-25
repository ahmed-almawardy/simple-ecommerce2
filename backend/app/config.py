from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = "sqlite:///./shop.db"
    JWT_SECRET: str = "dev-secret-change-me"
    JWT_EXPIRE_MINUTES: int = 60 * 24 * 7

    FRONTEND_URL: str = "http://localhost:3000"
    CORS_ORIGINS: str = "http://localhost:3000"

    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    CURRENCY: str = "usd"

    SMTP_HOST: str = ""
    SMTP_PORT: int = 1025
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_TLS: bool = False
    EMAIL_FROM: str = "VOLTA Home <no-reply@volta.local>"

    ABANDONED_CART_MINUTES: int = 60
    REMINDER_CHECK_INTERVAL_MINUTES: int = 5
    BRAND: str = "VOLTA"


settings = Settings()
