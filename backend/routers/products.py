from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models import Product, Manufacturer, Review

router = APIRouter(prefix="/api/products", tags=["商品"])


CATEGORIES = ["球类", "服装", "器材", "鞋类", "配件"]


@router.get("/categories")
def get_categories():
    return [{"value": c, "label": c} for c in CATEGORIES]


@router.get("/")
def list_products(
    category: str = Query(None), sort: str = Query(None),
    min_price: float = Query(None), max_price: float = Query(None),
    page: int = Query(1), page_size: int = Query(12),
    db: Session = Depends(get_db),
):
    q = db.query(Product)
    if category:
        q = q.filter(Product.category == category)
    if min_price is not None:
        q = q.filter(Product.unit_price >= min_price)
    if max_price is not None:
        q = q.filter(Product.unit_price <= max_price)
    if sort == "price_asc":
        q = q.order_by(Product.unit_price.asc())
    elif sort == "price_desc":
        q = q.order_by(Product.unit_price.desc())
    elif sort == "sales":
        q = q.order_by(Product.sales_count.desc())
    elif sort == "newest":
        q = q.order_by(Product.created_at.desc())
    total = q.count()
    total_pages = max(1, (total + page_size - 1) // page_size)
    products = q.offset((page - 1) * page_size).limit(page_size).all()
    return {
        "items": products,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1,
    }


@router.get("/hot")
def hot_products(limit: int = Query(6), db: Session = Depends(get_db)):
    return db.query(Product).order_by(Product.sales_count.desc()).limit(limit).all()


@router.get("/{product_id}")
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    mfr = db.query(Manufacturer).filter(Manufacturer.manufacturer_id == product.manufacturer_id).first()
    avg_r = db.query(func.avg(Review.rating)).filter(Review.product_id == product_id).scalar()
    rev_count = db.query(func.count(Review.review_id)).filter(Review.product_id == product_id).scalar()
    return {
        "product_id": product.product_id, "manufacturer_id": product.manufacturer_id,
        "manufacturer_name": mfr.manufacturer_name if mfr else "",
        "product_name": product.product_name, "category": product.category,
        "unit_price": float(product.unit_price), "stock_quantity": product.stock_quantity,
        "min_stock_threshold": product.min_stock_threshold,
        "sales_count": product.sales_count, "description": product.description,
        "avg_rating": round(float(avg_r), 1) if avg_r else 0.0,
        "review_count": rev_count or 0,
    }


@router.get("/search/")
def search_products(
    keyword: str, page: int = Query(1), page_size: int = Query(12),
    db: Session = Depends(get_db),
):
    q = db.query(Product).filter(
        Product.product_name.contains(keyword) | Product.description.contains(keyword)
    )
    total = q.count()
    total_pages = max(1, (total + page_size - 1) // page_size)
    products = q.offset((page - 1) * page_size).limit(page_size).all()
    return {
        "items": products, "total": total, "page": page,
        "page_size": page_size, "total_pages": total_pages,
        "has_next": page < total_pages, "has_prev": page > 1,
    }
