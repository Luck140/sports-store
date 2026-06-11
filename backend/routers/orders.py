from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from models import Order, OrderDetail, Product, Customer, Payment, StockRecord, Notification
from schemas import OrderCreate, OrderResponse, OrderDetailResponse
from datetime import datetime
import redis
import json

router = APIRouter(prefix="/api/orders", tags=["订单"])
redis_client = redis.StrictRedis(host="localhost", port=6379, db=0, charset="utf-8", decode_responses=True)


def add_notification(db, customer_id, title, content, notify_type, related_id=None):
    db.add(Notification(customer_id=customer_id, title=title, content=content,
                         notify_type=notify_type, related_id=related_id))
    db.commit()


@router.post("/")
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
            "quantity": item.quantity, "unit_price": float(product.unit_price),
            "total_amount": amount, "product_name_snapshot": product.product_name,
        })
    shipping_cost = 0
    if data.total_weight and data.total_weight > 0:
        shipping_cost = round(float(data.total_weight) * 10, 2)
        total += shipping_cost
    order = Order(
        customer_id=data.customer_id, total_amount=total, shipping_req=data.shipping_req,
        total_weight=data.total_weight, shipping_cost=shipping_cost,
        status="PENDING", payment_status=0,
        recipient_name=data.recipient_name, recipient_address=data.recipient_address,
        recipient_phone=data.recipient_phone, invoice_required=data.invoice_required,
        invoice_title=data.invoice_title, invoice_tax_no=data.invoice_tax_no,
    )
    db.add(order)
    db.flush()
    for d in detail_records:
        db.add(OrderDetail(order_id=order.order_id, product_id=d["product_id"],
                           product_name_snapshot=d["product_name_snapshot"],
                           manufacturer_id=d["manufacturer_id"], quantity=d["quantity"],
                           unit_price=d["unit_price"], total_amount=d["total_amount"]))
    db.commit()
    db.refresh(order)
    redis_client.delete(f"cart:{data.customer_id}")
    add_notification(db, data.customer_id, "订单创建成功",
                     f"您的订单 #{order.order_id} 已创建，金额 ¥{total:.2f}，请等待管理员确认。",
                     "order_status", order.order_id)
    return order


@router.get("/{order_id}")
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    customer = db.query(Customer).filter(Customer.customer_id == order.customer_id).first()
    return {
        "order_id": order.order_id, "customer_id": order.customer_id,
        "customer_name": customer.customer_name if customer else "",
        "order_date": order.order_date, "total_amount": float(order.total_amount),
        "shipping_cost": float(order.shipping_cost) if order.shipping_cost else 0,
        "total_weight": float(order.total_weight) if order.total_weight else 0,
        "status": order.status, "payment_status": order.payment_status,
        "recipient_name": order.recipient_name, "recipient_address": order.recipient_address,
        "recipient_phone": order.recipient_phone, "shipping_req": order.shipping_req,
        "invoice_required": order.invoice_required, "invoice_title": order.invoice_title,
        "invoice_tax_no": order.invoice_tax_no, "shipping_date": order.shipping_date,
    }


@router.get("/{order_id}/details")
def get_order_details(order_id: int, db: Session = Depends(get_db)):
    details = db.query(OrderDetail).filter(OrderDetail.order_id == order_id).all()
    result = []
    for d in details:
        product = db.query(Product).filter(Product.product_id == d.product_id).first()
        result.append(OrderDetailResponse(
            detail_id=d.detail_id, order_id=d.order_id, product_id=d.product_id,
            product_name=product.product_name if product else (d.product_name_snapshot or ""),
            product_name_snapshot=d.product_name_snapshot,
            quantity=d.quantity, unit_price=float(d.unit_price), total_amount=float(d.total_amount),
        ))
    return result


@router.get("/{order_id}/timeline")
def get_order_timeline(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    timeline = []
    timeline.append({"time": order.order_date, "icon": "cart", "title": "订单创建", "desc": "订单已提交"})
    payments = db.query(Payment).filter(Payment.order_id == order_id, Payment.status == "SUCCESS").all()
    for p in payments:
        timeline.append({"time": p.payment_time, "icon": "wallet", "title": "支付成功",
                         "desc": f"{p.payment_method} 支付 ¥{float(p.amount):.2f}"})
    if order.status in ("CONFIRMED", "SHIPPED", "COMPLETED", "OUT_OF_STOCK"):
        timeline.append({"time": order.updated_at, "icon": "check", "title": "订单已确认", "desc": "管理员已确认订单"})
    if order.status in ("SHIPPED", "COMPLETED"):
        desc = f"运费 ¥{float(order.shipping_cost):.2f}" if order.shipping_cost else "已发货"
        timeline.append({"time": order.shipping_date or order.updated_at, "icon": "truck",
                         "title": "已发货", "desc": desc})
    if order.status == "COMPLETED":
        timeline.append({"time": order.updated_at, "icon": "home", "title": "已收货", "desc": "订单已完成"})
    if order.status == "CANCELLED":
        timeline.append({"time": order.updated_at, "icon": "close", "title": "已取消", "desc": "订单已取消"})
    return timeline


@router.get("/customer/{customer_id}")
def list_customer_orders(
    customer_id: int, status: str = Query(None),
    keyword: str = Query(None), page: int = Query(1), page_size: int = Query(10),
    db: Session = Depends(get_db),
):
    q = db.query(Order).filter(Order.customer_id == customer_id)
    if status:
        q = q.filter(Order.status == status)
    if keyword:
        try:
            oid = int(keyword)
            q = q.filter(Order.order_id == oid)
        except ValueError:
            pass
    total = q.count()
    total_pages = max(1, (total + page_size - 1) // page_size)
    orders = q.order_by(Order.order_id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    result = []
    for o in orders:
        customer = db.query(Customer).filter(Customer.customer_id == o.customer_id).first()
        result.append({
            "order_id": o.order_id, "customer_id": o.customer_id,
            "customer_name": customer.customer_name if customer else "",
            "order_date": o.order_date, "total_amount": float(o.total_amount),
            "shipping_cost": float(o.shipping_cost) if o.shipping_cost else 0,
            "total_weight": float(o.total_weight) if o.total_weight else 0,
            "status": o.status, "payment_status": o.payment_status,
            "recipient_name": o.recipient_name, "recipient_address": o.recipient_address,
            "recipient_phone": o.recipient_phone, "shipping_req": o.shipping_req,
            "invoice_required": o.invoice_required, "invoice_title": o.invoice_title,
            "invoice_tax_no": o.invoice_tax_no,
        })
    return {"items": result, "total": total, "page": page, "page_size": page_size,
            "total_pages": total_pages, "has_next": page < total_pages, "has_prev": page > 1}


# 顾客自行取消订单
@router.post("/{order_id}/customer-cancel")
def customer_cancel_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    if order.status != "PENDING":
        raise HTTPException(status_code=400, detail="仅待确认的订单可以取消")
    order.status = "CANCELLED"
    db.commit()
    add_notification(db, order.customer_id, "订单已取消",
                     f"您的订单 #{order_id} 已取消。", "order_status", order_id)
    return {"message": "订单已取消"}


# 确认收货
@router.post("/{order_id}/confirm-receipt")
def confirm_receipt(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    if order.status != "SHIPPED":
        raise HTTPException(status_code=400, detail="仅已发货的订单可以确认收货")
    order.status = "COMPLETED"
    details = db.query(OrderDetail).filter(OrderDetail.order_id == order_id).all()
    for d in details:
        db.query(Product).filter(Product.product_id == d.product_id).update(
            {"sales_count": Product.sales_count + d.quantity})
    db.commit()
    add_notification(db, order.customer_id, "确认收货",
                     f"您已确认收到订单 #{order_id}，可以对已购商品进行评价。", "order_status", order_id)
    return {"message": "收货确认成功"}


# 催单
@router.post("/{order_id}/urge")
def urge_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    if order.status not in ("PENDING", "CONFIRMED"):
        raise HTTPException(status_code=400, detail="仅待确认或已确认的订单可以催单")
    return {"message": "已发送催单提醒，我们会尽快处理您的订单"}
