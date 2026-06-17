from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Product
import redis, json

router = APIRouter(prefix="/api/cart", tags=["购物车"])
rc = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)


@router.get("/{customer_id}")
def get_cart(customer_id: int, db: Session = Depends(get_db)):
    data = rc.get(f"cart:{customer_id}")
    cart = json.loads(data) if data else {"items": []}
    tp = 0.0
    items = []
    for it in cart["items"]:
        p = db.query(Product).filter(Product.product_id == it["product_id"]).first()
        nm = p.product_name if p else "已下架"
        pr = float(p.unit_price) if p else 0
        sb = round(pr * it["quantity"], 2)
        tp += sb
        items.append({"product_id": it["product_id"], "product_name": nm, "unit_price": pr,
                      "quantity": it["quantity"], "subtotal": sb, "stock_quantity": p.stock_quantity if p else 0})
    return {"items": items, "total_price": round(tp, 2), "item_count": sum(i["quantity"] for i in items)}


@router.post("/{customer_id}/add")
def add_to_cart(customer_id: int, product_id: int, quantity: int = 1, db: Session = Depends(get_db)):
    if not db.query(Product).filter(Product.product_id == product_id).first():
        raise HTTPException(404, detail="商品不存在")
    data = rc.get(f"cart:{customer_id}")
    cart = json.loads(data) if data else {"items": []}
    for it in cart["items"]:
        if it["product_id"] == product_id: it["quantity"] += quantity; break
    else:
        cart["items"].append({"product_id": product_id, "quantity": quantity})
    rc.set(f"cart:{customer_id}", json.dumps(cart))
    return cart


@router.put("/{customer_id}/update/{product_id}")
def update_qty(customer_id: int, product_id: int, quantity: int = 1, db: Session = Depends(get_db)):
    if quantity < 1: raise HTTPException(400, detail="数量至少为1")
    data = rc.get(f"cart:{customer_id}")
    if not data: raise HTTPException(404, detail="购物车为空")
    cart = json.loads(data)
    for it in cart["items"]:
        if it["product_id"] == product_id:
            p = db.query(Product).filter(Product.product_id == product_id).first()
            if p and quantity > p.stock_quantity: raise HTTPException(400, detail=f"库存不足，最多{p.stock_quantity}件")
            it["quantity"] = quantity
            rc.set(f"cart:{customer_id}", json.dumps(cart))
            return cart
    raise HTTPException(404, detail="商品不在购物车中")


@router.delete("/{customer_id}/remove/{product_id}")
def remove_item(customer_id: int, product_id: int):
    data = rc.get(f"cart:{customer_id}")
    if not data: raise HTTPException(404, detail="购物车为空")
    cart = json.loads(data)
    cart["items"] = [i for i in cart["items"] if i["product_id"] != product_id]
    rc.set(f"cart:{customer_id}", json.dumps(cart))
    return cart


@router.delete("/{customer_id}/clear")
def clear_cart(customer_id: int):
    rc.delete(f"cart:{customer_id}")
    return {"message": "已清空"}


@router.get("/{customer_id}/count")
def cart_count(customer_id: int):
    data = rc.get(f"cart:{customer_id}")
    return {"count": len(json.loads(data).get("items", [])) if data else 0}
