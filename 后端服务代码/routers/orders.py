from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from models import Order, OrderDetail, Product, Payment, Notification, Customer, Manufacturer
from schemas import OrderCreate, OrderDetailResponse
import redis, json

router = APIRouter(prefix="/api/orders", tags=["订单"])
rc = redis.StrictRedis(host="localhost", port=6379, db=0, decode_responses=True)


def ntf(db, cid, title, content, nt, rid=None):
    db.add(Notification(customer_id=cid, title=title, content=content, notify_type=nt, related_id=rid))
    db.commit()


@router.post("/")
def create_order(data: OrderCreate, db: Session = Depends(get_db)):
    total = 0.0
    dets = []
    for it in data.items:
        p = db.query(Product).filter(Product.product_id == it.product_id).first()
        if not p: raise HTTPException(404, detail=f"商品{it.product_id}不存在")
        amt = float(p.unit_price) * it.quantity
        total += amt
        dets.append({"product_id": it.product_id, "manufacturer_id": it.manufacturer_id,
                     "quantity": it.quantity, "unit_price": float(p.unit_price),
                     "total_amount": amt, "product_name_snapshot": p.product_name})
    sc = 0
    if data.total_weight and float(data.total_weight) > 0:
        sc = round(float(data.total_weight) * 10, 2)
        total += sc
    o = Order(customer_id=data.customer_id, total_amount=total, shipping_req=data.shipping_req,
              total_weight=data.total_weight, shipping_cost=sc, status="PENDING", payment_status=0,
              recipient_name=data.recipient_name, recipient_address=data.recipient_address,
              recipient_phone=data.recipient_phone, invoice_required=data.invoice_required,
              invoice_title=data.invoice_title, invoice_tax_no=data.invoice_tax_no,
              invoice_address_phone=data.invoice_address_phone, invoice_bank=data.invoice_bank)
    db.add(o); db.flush()
    for d in dets:
        db.add(OrderDetail(order_id=o.order_id, **d))
    db.commit(); db.refresh(o)
    rc.delete(f"cart:{data.customer_id}")
    ntf(db, data.customer_id, "订单创建成功", f"订单#{o.order_id}已创建", "order_status", o.order_id)
    return {"order_id": o.order_id, "total_amount": float(o.total_amount),
            "status": o.status, "payment_status": o.payment_status}


@router.get("/{order_id}")
def get_order(order_id: int, db: Session = Depends(get_db)):
    o = db.query(Order).filter(Order.order_id == order_id).first()
    if not o: raise HTTPException(404, detail="订单不存在")
    c = db.query(Customer).filter(Customer.customer_id == o.customer_id).first()
    return {"order_id": o.order_id, "customer_id": o.customer_id,
            "customer_name": c.customer_name if c else "", "order_date": o.order_date,
            "total_amount": float(o.total_amount), "shipping_cost": float(o.shipping_cost) if o.shipping_cost else 0,
            "total_weight": float(o.total_weight) if o.total_weight else 0,
            "status": o.status, "payment_status": o.payment_status,
            "recipient_name": o.recipient_name, "recipient_address": o.recipient_address,
            "recipient_phone": o.recipient_phone, "shipping_req": o.shipping_req,
            "invoice_required": o.invoice_required, "invoice_title": o.invoice_title,
            "invoice_tax_no": o.invoice_tax_no, "invoice_address_phone": o.invoice_address_phone,
            "invoice_bank": o.invoice_bank, "shipping_date": o.shipping_date}


@router.get("/{order_id}/details")
def get_details(order_id: int, db: Session = Depends(get_db)):
    res = []
    for d in db.query(OrderDetail).filter(OrderDetail.order_id == order_id).all():
        p = db.query(Product).filter(Product.product_id == d.product_id).first()
        res.append(OrderDetailResponse(detail_id=d.detail_id, order_id=d.order_id, product_id=d.product_id,
                    product_name=p.product_name if p else (d.product_name_snapshot or ""),
                    product_name_snapshot=d.product_name_snapshot, quantity=d.quantity,
                    unit_price=float(d.unit_price), total_amount=float(d.total_amount)))
    return res


@router.get("/{order_id}/timeline")
def get_timeline(order_id: int, db: Session = Depends(get_db)):
    o = db.query(Order).filter(Order.order_id == order_id).first()
    if not o: raise HTTPException(404, detail="订单不存在")
    tl = [{"time": o.order_date, "icon": "cart", "title": "订单创建", "desc": "订单已提交"}]
    for p in db.query(Payment).filter(Payment.order_id == order_id, Payment.status == "SUCCESS").all():
        tl.append({"time": p.payment_time, "icon": "wallet", "title": "支付成功",
                   "desc": f"{p.payment_method} ¥{float(p.amount):.2f}"})
    if o.status in ("CONFIRMED", "SHIPPED", "COMPLETED", "OUT_OF_STOCK"):
        tl.append({"time": o.updated_at, "icon": "check", "title": "已确认", "desc": "管理员已确认"})
    if o.status in ("SHIPPED", "COMPLETED"):
        tl.append({"time": o.shipping_date or o.updated_at, "icon": "truck",
                   "title": "已发货", "desc": f"运费¥{float(o.shipping_cost):.2f}" if o.shipping_cost else "已发货"})
    if o.status == "COMPLETED":
        tl.append({"time": o.updated_at, "icon": "home", "title": "已收货", "desc": "订单已完成"})
    if o.status == "CANCELLED":
        tl.append({"time": o.updated_at, "icon": "close", "title": "已取消", "desc": "订单已取消"})
    return tl


@router.get("/customer/{customer_id}")
def list_customer_orders(customer_id: int, status: str = None, keyword: str = None,
                         page: int = 1, page_size: int = 10, db: Session = Depends(get_db)):
    q = db.query(Order).filter(Order.customer_id == customer_id)
    if status: q = q.filter(Order.status == status)
    if keyword:
        try: q = q.filter(Order.order_id == int(keyword))
        except ValueError: pass
    total = q.count()
    tp = max(1, (total + page_size - 1) // page_size)
    items = []
    for o in q.order_by(Order.order_id.desc()).offset((page - 1) * page_size).limit(page_size).all():
        c = db.query(Customer).filter(Customer.customer_id == o.customer_id).first()
        # 获取订单商品明细
        order_items = []
        for d in db.query(OrderDetail).filter(OrderDetail.order_id == o.order_id).all():
            p = db.query(Product).filter(Product.product_id == d.product_id).first()
            order_items.append({
                "product_id": d.product_id,
                "product_name": p.product_name if p else (d.product_name_snapshot or ""),
                "quantity": d.quantity,
                "unit_price": float(d.unit_price),
                "total_amount": float(d.total_amount),
            })
        items.append({"order_id": o.order_id, "customer_id": o.customer_id,
                      "customer_name": c.customer_name if c else "",
                      "order_date": o.order_date, "total_amount": float(o.total_amount),
                      "shipping_cost": float(o.shipping_cost) if o.shipping_cost else 0,
                      "status": o.status, "payment_status": o.payment_status,
                      "items": order_items})
    return {"items": items, "total": total, "page": page, "page_size": page_size,
            "total_pages": tp, "has_next": page < tp, "has_prev": page > 1}


@router.post("/{order_id}/customer-cancel")
def customer_cancel(order_id: int, db: Session = Depends(get_db)):
    o = db.query(Order).filter(Order.order_id == order_id).first()
    if not o or o.status != "PENDING": raise HTTPException(400, detail="仅待确认订单可取消")
    o.status = "CANCELLED"; db.commit()
    ntf(db, o.customer_id, "订单已取消", f"订单#{order_id}已取消", "order_status", order_id)
    return {"message": "已取消"}


@router.post("/{order_id}/confirm-receipt")
def confirm_receipt(order_id: int, db: Session = Depends(get_db)):
    o = db.query(Order).filter(Order.order_id == order_id).first()
    if not o or o.status != "SHIPPED": raise HTTPException(400, detail="仅已发货订单可确认收货")
    o.status = "COMPLETED"
    for d in db.query(OrderDetail).filter(OrderDetail.order_id == order_id).all():
        db.query(Product).filter(Product.product_id == d.product_id).update(
            {"sales_count": Product.sales_count + d.quantity})
    db.commit()
    ntf(db, o.customer_id, "已收货", f"订单#{order_id}已完成", "order_status", order_id)
    return {"message": "收货成功"}


@router.post("/{order_id}/urge")
def urge_order(order_id: int, db: Session = Depends(get_db)):
    o = db.query(Order).filter(Order.order_id == order_id).first()
    if not o or o.status not in ("PENDING", "CONFIRMED"):
        raise HTTPException(400, detail="仅待确认/已确认订单可催单")
    return {"message": "已催单"}
