from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Order, OrderDetail, Product, Customer
from schemas import OrderCreate, OrderResponse, OrderDetailResponse
import redis
import json

router = APIRouter(prefix="/api/orders", tags=["订单"])
redis_client = redis.StrictRedis(host="localhost", port=6379, db=0, charset="utf-8", decode_responses=True)


@router.post("/", response_model=OrderResponse)
def create_order(data: OrderCreate, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.customer_id == data.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="顾客不存在")
    total = 0.0
    detail_records = []
    for item in data.items:
        product = db.query(Product).filter(Product.product_id == item.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"商品 {item.product_id} 不存在")
        amount = float(product.unit_price) * item.quantity
        total += amount
        detail_records.append({
            "product_id": item.product_id, "manufacturer_id": item.manufacturer_id,
            "quantity": item.quantity, "unit_price": float(product.unit_price), "total_amount": amount,
        })
    order = Order(
        customer_id=data.customer_id, total_amount=total, shipping_req=data.shipping_req,
        status="PENDING", payment_status=0,
        recipient_name=data.recipient_name, recipient_address=data.recipient_address,
        recipient_phone=data.recipient_phone, invoice_required=data.invoice_required,
        invoice_title=data.invoice_title, invoice_tax_no=data.invoice_tax_no,
    )
    db.add(order)
    db.flush()
    for d in detail_records:
        db.add(OrderDetail(order_id=order.order_id, product_id=d["product_id"],
                           manufacturer_id=d["manufacturer_id"], quantity=d["quantity"],
                           unit_price=d["unit_price"], total_amount=d["total_amount"]))
    db.commit()
    db.refresh(order)
    redis_client.delete(f"cart:{data.customer_id}")
    return order


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    return order


@router.get("/{order_id}/details")
def get_order_details(order_id: int, db: Session = Depends(get_db)):
    details = db.query(OrderDetail).filter(OrderDetail.order_id == order_id).all()
    result = []
    for d in details:
        product = db.query(Product).filter(Product.product_id == d.product_id).first()
        result.append(OrderDetailResponse(
            detail_id=d.detail_id, order_id=d.order_id, product_id=d.product_id,
            product_name=product.product_name if product else "",
            quantity=d.quantity, unit_price=float(d.unit_price), total_amount=float(d.total_amount),
        ))
    return result


@router.get("/customer/{customer_id}")
def list_customer_orders(customer_id: int, db: Session = Depends(get_db)):
    return db.query(Order).filter(Order.customer_id == customer_id).order_by(Order.order_id.desc()).all()