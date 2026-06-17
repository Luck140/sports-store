from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models import Product, Manufacturer, Review

router = APIRouter(prefix="/api/products", tags=["商品"])

CATS = ["球类", "服装", "器材", "鞋类", "配件"]


@router.get("/categories")
def get_categories():
    return [{"value": c, "label": c} for c in CATS]


@router.get("/")
def list_products(category: str = None, sort: str = None,
                  min_price: float = None, max_price: float = None,
                  page: int = 1, page_size: int = 12, db: Session = Depends(get_db)):
    q = db.query(Product)
    if category: q = q.filter(Product.category == category)
    if min_price is not None: q = q.filter(Product.unit_price >= min_price)
    if max_price is not None: q = q.filter(Product.unit_price <= max_price)
    sm = {"price_asc": Product.unit_price.asc(), "price_desc": Product.unit_price.desc(),
          "sales": Product.sales_count.desc(), "newest": Product.created_at.desc()}
    if sort in sm: q = q.order_by(sm[sort])
    total = q.count()
    tp = max(1, (total + page_size - 1) // page_size)
    items = q.offset((page - 1) * page_size).limit(page_size).all()
    return {"items": items, "total": total, "page": page, "page_size": page_size,
            "total_pages": tp, "has_next": page < tp, "has_prev": page > 1}


@router.get("/hot")
def hot_products(limit: int = 6, db: Session = Depends(get_db)):
    return db.query(Product).order_by(Product.sales_count.desc()).limit(limit).all()


@router.get("/search/")
def search(keyword: str, page: int = 1, page_size: int = 12, db: Session = Depends(get_db)):
    q = db.query(Product).filter(
        Product.product_name.contains(keyword) | Product.description.contains(keyword))
    total = q.count()
    tp = max(1, (total + page_size - 1) // page_size)
    items = q.offset((page - 1) * page_size).limit(page_size).all()
    return {"items": items, "total": total, "page": page, "page_size": page_size,
            "total_pages": tp, "has_next": page < tp, "has_prev": page > 1}


@router.get("/{product_id}")
def get_product(product_id: int, db: Session = Depends(get_db)):
    p = db.query(Product).filter(Product.product_id == product_id).first()
    if not p: raise HTTPException(404, detail="商品不存在")
    m = db.query(Manufacturer).filter(Manufacturer.manufacturer_id == p.manufacturer_id).first()
    ar = db.query(func.avg(Review.rating)).filter(Review.product_id == product_id).scalar()
    rc = db.query(func.count(Review.review_id)).filter(Review.product_id == product_id).scalar()
    return {"product_id": p.product_id, "manufacturer_id": p.manufacturer_id,
            "manufacturer_name": m.manufacturer_name if m else "",
            "product_name": p.product_name, "category": p.category,
            "unit_price": float(p.unit_price), "stock_quantity": p.stock_quantity,
            "min_stock_threshold": p.min_stock_threshold,
            "sales_count": p.sales_count, "description": p.description,
            "avg_rating": round(float(ar), 1) if ar else 0.0, "review_count": rc or 0}
