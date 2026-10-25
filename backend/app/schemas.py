from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ORM(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ---------- auth ----------
class RegisterIn(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class UserOut(ORM):
    id: int
    email: str
    full_name: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ---------- catalog ----------
class CategoryOut(ORM):
    id: int
    name: str
    slug: str
    image_url: str


class ProductOut(ORM):
    id: int
    name: str
    slug: str
    description: str
    price_cents: int
    image_url: str
    images: list[str]
    stock: int
    brand: str
    energy_rating: str
    warranty_months: int
    specs: dict[str, str]
    category: CategoryOut


class ProductList(BaseModel):
    items: list[ProductOut]
    total: int
    page: int
    page_size: int


class FacetsOut(BaseModel):
    brands: list[str]
    energy_ratings: list[str]
    min_price_cents: int
    max_price_cents: int


# ---------- cart ----------
class CartAddIn(BaseModel):
    product_id: int
    quantity: int = Field(default=1, ge=1, le=20)


class CartUpdateIn(BaseModel):
    quantity: int = Field(ge=0, le=20)


class CartItemOut(ORM):
    product: ProductOut
    quantity: int
    line_total_cents: int = 0


class CartOut(BaseModel):
    items: list[CartItemOut]
    total_cents: int
    count: int


# ---------- orders ----------
class CheckoutIn(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    address: str = Field(min_length=3, max_length=255)
    city: str = Field(min_length=1, max_length=120)
    postal_code: str = Field(min_length=2, max_length=20)
    country: str = Field(min_length=2, max_length=80)


class OrderItemOut(ORM):
    product_id: int
    name: str
    image_url: str
    unit_price_cents: int
    quantity: int


class OrderOut(ORM):
    id: int
    status: str
    total_cents: int
    created_at: datetime
    paid_at: datetime | None
    full_name: str
    address: str
    city: str
    postal_code: str
    country: str
    items: list[OrderItemOut]


class CheckoutOut(BaseModel):
    order_id: int
    payment_url: str


class ConfirmIn(BaseModel):
    session_id: str
