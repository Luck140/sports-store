from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Product
import redis
import json

router = APIRouter(prefix="/api/cart", tags=["购物车"])
redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)


def _cart_key(customer_id: int) -> str:
    return f"cart:{customer_id}"


@router.get("/{customer_id}")
def get_cart(customer_id: int, db: Session = Depends(get_db)):
    cart_data = redis_client.get(_cart_key(customer_id))
    cart = json.loads(cart_data) if cart_data else {"items": []}
    total_price = 0.0
    enriched_items = []
    for item in cart["items"]:
        product = db.query(Product).filter(Product.product_id == item["product_id"]).first()
        name = product.product_name if product else "商品已下架"
        price = float(product.unit_price) if product else 0.0
        stock = product.stock_quantity if product else 0
        subtotal = round(price * item["quantity"], 2)
        total_price += subtotal
        enriched_items.append({
            "product_id": item["product_id"], "product_name": name,
            "unit_price": price, "quantity": item["quantity"],
            "subtotal": subtotal, "stock_quantity": stock,
        })
    return {"items": enriched_items, "total_price": round(total_price, 2),
            "item_count": sum(i["quantity"] for i in enriched_items)}


@router.post("/{customer_id}/add")
def add_to_cart(customer_id: int, product_id: int, quantity: int = 1, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    cart_data = redis_client.get(_cart_key(customer_id))
    cart = json.loads(cart_data) if cart_data else {"items": []}
    for item in cart["items"]:
        if item["product_id"] == product_id:
            item["quantity"] += quantity
            break
    else:
        cart["items"].append({"product_id": product_id, "quantity": quantity})
    redis_client.set(_cart_key(customer_id), json.dumps(cart))
    return cart


@router.put("/{customer_id}/update/{product_id}")
def update_cart_quantity(customer_id: int, product_id: int, quantity: int = 1, db: Session = Depends(get_db)):
    if quantity < 1:
        raise HTTPException(status_code=400, detail="数量至少为1")
    cart_data = redis_client.get(_cart_key(customer_id))
    if not cart_data:
        raise HTTPException(status_code=404, detail="购物车为空")
    cart = json.loads(cart_data)
    for item in cart["items"]:
        if item["product_id"] == product_id:
            product = db.query(Product).filter(Product.product_id == product_id).first()
            if product and quantity > product.stock_quantity:
                raise HTTPException(status_code=400, detail=f"库存不足，最多可购买 {product.stock_quantity} 件")
            item["quantity"] = quantity
            redis_client.set(_cart_key(customer_id), json.dumps(cart))
            return cart
    raise HTTPException(status_code=404, detail="商品不在购物车中")


@router.delete("/{customer_id}/remove/{product_id}")
def remove_from_cart(customer_id: int, product_id: int):
    cart_data = redis_client.get(_cart_key(customer_id))
    if not cart_data:
        raise HTTPException(status_code=404, detail="购物车为空")
    cart = json.loads(cart_data)
    cart["items"] = [item for item in cart["items"] if item["product_id"] != product_id]
    redis_client.set(_cart_key(customer_id), json.dumps(cart))
    return cart


@router.delete("/{customer_id}/clear")
def clear_cart(customer_id: int):
    redis_client.delete(_cart_key(customer_id))
    return {"message": "购物车已清空"}


@router.get("/{customer_id}/count")
def cart_count(customer_id: int):
    cart_data = redis_client.get(_cart_key(customer_id))
    if not cart_data:
        return {"count": 0}
    cart = json.loads(cart_data)
    count = len(cart["items"]) if "items" in cart else 0
    return {"count": count}
