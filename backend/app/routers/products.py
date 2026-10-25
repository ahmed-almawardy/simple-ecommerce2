from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from ..database import get_db
from ..models import Category, Product
from ..schemas import CategoryOut, FacetsOut, ProductList, ProductOut

router = APIRouter(prefix="/api", tags=["catalog"])

SORTS = {
    "newest": Product.created_at.desc(),
    "price_asc": Product.price_cents.asc(),
    "price_desc": Product.price_cents.desc(),
    "name": Product.name.asc(),
}


@router.get("/categories", response_model=list[CategoryOut])
def categories(db: Session = Depends(get_db)):
    return db.scalars(select(Category).order_by(Category.id)).all()


@router.get("/products", response_model=ProductList)
def list_products(
    category: str | None = None,
    q: str | None = None,
    brand: list[str] | None = Query(default=None),
    energy: list[str] | None = Query(default=None, description="energy ratings, e.g. A"),
    min_price: int | None = Query(default=None, ge=0, description="in dollars"),
    max_price: int | None = Query(default=None, ge=0, description="in dollars"),
    in_stock: bool = False,
    sort: str = "newest",
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=12, ge=1, le=60),
    db: Session = Depends(get_db),
):
    stmt = select(Product).options(joinedload(Product.category))
    if category:
        stmt = stmt.join(Category).where(Category.slug == category)
    if q:
        like = f"%{q.strip()}%"
        stmt = stmt.where(Product.name.ilike(like) | Product.description.ilike(like))
    if brand:
        stmt = stmt.where(Product.brand.in_(brand))
    if energy:
        stmt = stmt.where(Product.energy_rating.in_(energy))
    if min_price is not None:
        stmt = stmt.where(Product.price_cents >= min_price * 100)
    if max_price is not None:
        stmt = stmt.where(Product.price_cents <= max_price * 100)
    if in_stock:
        stmt = stmt.where(Product.stock > 0)

    total = db.scalar(select(func.count()).select_from(stmt.order_by(None).subquery()))
    stmt = stmt.order_by(SORTS.get(sort, SORTS["newest"]), Product.id).offset((page - 1) * page_size).limit(page_size)
    items = db.scalars(stmt).unique().all()
    return ProductList(items=items, total=total or 0, page=page, page_size=page_size)


@router.get("/facets", response_model=FacetsOut)
def facets(category: str | None = None, db: Session = Depends(get_db)):
    base = select(Product)
    if category:
        base = base.join(Category).where(Category.slug == category)
    sub = base.subquery()
    brands = db.scalars(select(sub.c.brand).distinct().order_by(sub.c.brand)).all()
    ratings = db.scalars(select(sub.c.energy_rating).distinct().order_by(sub.c.energy_rating)).all()
    lo, hi = db.execute(select(func.min(sub.c.price_cents), func.max(sub.c.price_cents))).one()
    return FacetsOut(brands=[b for b in brands if b], energy_ratings=[r for r in ratings if r], min_price_cents=lo or 0, max_price_cents=hi or 0)


@router.get("/products/{slug}", response_model=ProductOut)
def get_product(slug: str, db: Session = Depends(get_db)):
    product = db.scalar(select(Product).options(joinedload(Product.category)).where(Product.slug == slug))
    if not product:
        raise HTTPException(404, "Product not found")
    return product
