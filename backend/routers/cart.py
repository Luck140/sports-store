# routers/cart.py - 购物车（Redis 缓存）
from fastapi import APIRouter, HTTPException
import redis
import json

router = APIRouter(prefix="/api/cart", tags=["购物车"])

# Redis 连接（默认本地 6379）
redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)


def _cart_key(customer_id: int) -> str:
    return f"cart:{customer_id}"


@router.get("/{customer_id}")
def get_cart(customer_id: int):
    cart_data = redis_client.get(_cart_key(customer_id))
    if cart_data:
        return json.loads(cart_data)
    return {"items": []}


@router.post("/{customer_id}/add")
def add_to_cart(customer_id: int, product_id: int, quantity: int = 1):
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