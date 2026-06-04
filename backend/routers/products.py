from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Product, Manufacturer
from schemas import ProductResponse, ProductDetailResponse

router = APIRouter(prefix="/api/products", tags=["商品"])


@router.get("/", response_model=list[ProductResponse])
def list_products(db: Session = Depends(get_db)):
    return db.query(Product).all()


@router.get("/{product_id}", response_model=ProductDetailResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    mfr = db.query(Manufacturer).filter(Manufacturer.manufacturer_id == product.manufacturer_id).first()
    return ProductDetailResponse(
        product_id=product.product_id,
        manufacturer_id=product.manufacturer_id,
        manufacturer_name=mfr.manufacturer_name if mfr else "",
        product_name=product.product_name,
        unit_price=float(product.unit_price),
        stock_quantity=product.stock_quantity,
        min_stock_threshold=product.min_stock_threshold,
        description=product.description,
    )


@router.get("/search/")
def search_products(keyword: str, db: Session = Depends(get_db)):
    return db.query(Product).filter(Product.product_name.contains(keyword)).all()