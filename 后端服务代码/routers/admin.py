from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models import (Order, OrderDetail, Product, StockRecord, PurchaseOrder, PurchaseDetail,
                    Manufacturer, Customer, OperationLog, Notification)
from schemas import PurchaseOrderCreate, StockRecordResponse

router = APIRouter(prefix="/api/admin", tags=["管理员"])
import redis
rc = redis.StrictRedis(host="localhost", port=6379, db=0, decode_responses=True)


def log_op(db, oid, oname, optype, ttype, tid, detail=""):
    db.add(OperationLog(operator_id=oid, operator_name=oname, operation_type=optype,
                        target_type=ttype, target_id=tid, detail=detail)); db.commit()


def ntf(db, cid, title, content, nt, rid=None):
    db.add(Notification(customer_id=cid, title=title, content=content, notify_type=nt, related_id=rid))
    db.commit()


@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db)):
    pc = db.query(Order).filter(Order.status == "PENDING").count()
    rc_ = db.query(Order).filter(Order.status == "REFUNDING").count()
    ls = db.query(Product).filter(Product.stock_quantity < Product.min_stock_threshold).count()
    return {"total_orders": db.query(Order).count(), "pending_orders": pc,
            "unshipped_orders": db.query(Order).filter(Order.status.in_(["CONFIRMED", "OUT_OF_STOCK"])).count(),
            "low_stock_count": ls, "refunding_count": rc_, "today_orders": 0,
            "pending_todos": [
                {"type": "order", "count": pc, "label": "待确认订单", "link": "/admin/orders?status=PENDING"},
                {"type": "stock", "count": ls, "label": "库存预警商品", "link": "/admin/reports?type=lowstock"},
                {"type": "refund", "count": rc_, "label": "待审核退款", "link": "/admin/orders?status=REFUNDING"}]}


@router.get("/dashboard/sales-chart")
def sales_chart(db: Session = Depends(get_db)):
    rs = db.query(func.date_format(Order.order_date, "%Y-%m-%d").label("day"),
                  func.count(Order.order_id).label("cnt"),
                  func.coalesce(func.sum(Order.total_amount), 0).label("amt"))\
        .filter(Order.status.in_(["CONFIRMED", "SHIPPED", "COMPLETED"]))\
        .group_by("day").order_by(func.date(Order.order_date).desc()).limit(30).all()
    return [{"date": r.day, "count": r.cnt, "amount": float(r.amt)} for r in rs]


@router.get("/dashboard/hot-products")
def hot_products(db: Session = Depends(get_db)):
    return [{"product_id": p.product_id, "product_name": p.product_name, "sales_count": p.sales_count}
            for p in db.query(Product).order_by(Product.sales_count.desc()).limit(5).all()]


@router.post("/orders/{order_id}/confirm")
def confirm_order(order_id: int, db: Session = Depends(get_db)):
    o = db.query(Order).filter(Order.order_id == order_id).first()
    if not o or o.status != "PENDING": raise HTTPException(400, detail="仅待确认订单可确认")
    lock = rc.lock(f"lock:order:{order_id}", timeout=10)
    if not lock.acquire(blocking=True, blocking_timeout=5): raise HTTPException(409, detail="订单处理中")
    try:
        dets = db.query(OrderDetail).filter(OrderDetail.order_id == order_id).all()
        for d in dets:
            p = db.query(Product).filter(Product.product_id == d.product_id).first()
            if not p or p.stock_quantity < d.quantity:
                o.status = "OUT_OF_STOCK"; db.commit()
                return {"message": f"商品{d.product_id}库存不足", "status": "OUT_OF_STOCK"}
        for d in dets:
            db.query(Product).filter(Product.product_id == d.product_id).update(
                {"stock_quantity": Product.stock_quantity - d.quantity})
            db.add(StockRecord(product_id=d.product_id, quantity_change=-d.quantity, reason="ORDER_CONFIRM",
                               related_id=order_id, operated_by=1))
        o.status = "CONFIRMED"; db.commit()
        log_op(db, 1, "管理员", "CONFIRM_ORDER", "order", order_id, "确认成功")
        ntf(db, o.customer_id, "订单已确认", f"订单#{order_id}已确认", "order_status", order_id)
        return {"message": "确认成功", "status": "CONFIRMED"}
    finally:
        lock.release()


@router.post("/orders/{order_id}/ship")
def ship_order(order_id: int, db: Session = Depends(get_db)):
    o = db.query(Order).filter(Order.order_id == order_id).first()
    if not o or o.status != "CONFIRMED": raise HTTPException(400, detail="仅已确认订单可发货")
    if o.total_weight and float(o.total_weight) > 0:
        o.shipping_cost = round(float(o.total_weight) * 10, 2)
    o.status = "SHIPPED"; o.shipping_date = func.current_date()
    db.commit()
    log_op(db, 1, "管理员", "SHIP_ORDER", "order", order_id, f"运费¥{float(o.shipping_cost):.2f}")
    ntf(db, o.customer_id, "已发货", f"订单#{order_id}已发货", "order_status", order_id)
    return {"message": "发货成功", "shipping_cost": float(o.shipping_cost) if o.shipping_cost else 0}


@router.post("/orders/{order_id}/cancel")
def cancel_order(order_id: int, db: Session = Depends(get_db)):
    o = db.query(Order).filter(Order.order_id == order_id).first()
    if not o: raise HTTPException(404, detail="订单不存在")
    if o.status == "SHIPPED": raise HTTPException(400, detail="已发货订单不支持取消")
    if o.status == "CANCELLED": raise HTTPException(400, detail="已取消")
    if o.status == "CONFIRMED":
        for d in db.query(OrderDetail).filter(OrderDetail.order_id == order_id).all():
            db.query(Product).filter(Product.product_id == d.product_id).update(
                {"stock_quantity": Product.stock_quantity + d.quantity})
            db.add(StockRecord(product_id=d.product_id, quantity_change=d.quantity, reason="ORDER_CANCEL",
                               related_id=order_id, operated_by=1))
    o.status = "CANCELLED"; db.commit()
    log_op(db, 1, "管理员", "CANCEL_ORDER", "order", order_id, "取消订单")
    ntf(db, o.customer_id, "订单已取消", f"订单#{order_id}已取消", "order_status", order_id)
    return {"message": "已取消"}


@router.post("/orders/batch-confirm")
def batch_confirm(data: dict, db: Session = Depends(get_db)):
    res = []
    for oid in data.get("order_ids", []):
        try: confirm_order(oid, db); res.append({"order_id": oid, "status": "success"})
        except HTTPException as e: res.append({"order_id": oid, "status": "failed", "detail": e.detail})
    return {"results": res}


@router.post("/orders/batch-ship")
def batch_ship(data: dict, db: Session = Depends(get_db)):
    res = []
    for oid in data.get("order_ids", []):
        try: ship_order(oid, db); res.append({"order_id": oid, "status": "success"})
        except HTTPException as e: res.append({"order_id": oid, "status": "failed", "detail": e.detail})
    return {"results": res}


@router.get("/orders")
def list_all_orders(status: str = None, keyword: str = None, page: int = 1, page_size: int = 20,
                    db: Session = Depends(get_db)):
    q = db.query(Order)
    if status: q = q.filter(Order.status == status)
    if keyword:
        cids = [c.customer_id for c in db.query(Customer).filter(Customer.customer_name.contains(keyword)).all()]
        try: oid = int(keyword); q = q.filter((Order.order_id == oid) | (Order.customer_id.in_(cids)))
        except ValueError:
            if cids: q = q.filter(Order.customer_id.in_(cids))
    total = q.count()
    tp = max(1, (total + page_size - 1) // page_size)
    items = []
    for o in q.order_by(Order.order_id.desc()).offset((page - 1) * page_size).limit(page_size).all():
        c = db.query(Customer).filter(Customer.customer_id == o.customer_id).first()
        items.append({"order_id": o.order_id, "customer_id": o.customer_id,
                      "customer_name": c.customer_name if c else "", "customer_phone": c.phone if c else "",
                      "total_amount": float(o.total_amount), "status": o.status,
                      "payment_status": o.payment_status, "order_date": o.order_date})
    return {"items": items, "total": total, "page": page, "page_size": page_size,
            "total_pages": tp, "has_next": page < tp, "has_prev": page > 1}


@router.get("/customers/{customer_id}")
def get_customer_detail(customer_id: int, db: Session = Depends(get_db)):
    c = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if not c: raise HTTPException(404, detail="顾客不存在")
    ts = db.query(func.coalesce(func.sum(Order.total_amount), 0)).filter(
        Order.customer_id == customer_id, Order.payment_status.in_([1, 2])).scalar()
    return {"customer_id": c.customer_id, "customer_name": c.customer_name, "username": c.username,
            "phone": c.phone, "email": c.email, "address": c.address, "created_at": c.created_at,
            "total_orders": db.query(Order).filter(Order.customer_id == customer_id).count(),
            "total_spent": float(ts)}


@router.get("/purchases")
def list_purchases(db: Session = Depends(get_db)):
    return [{"purchase_id": p.purchase_id, "manufacturer_id": p.manufacturer_id,
             "manufacturer_name": (db.query(Manufacturer).filter(Manufacturer.manufacturer_id == p.manufacturer_id).first().manufacturer_name or "") if db.query(Manufacturer).filter(Manufacturer.manufacturer_id == p.manufacturer_id).first() else "",
             "total_amount": float(p.total_amount), "status": p.status}
            for p in db.query(PurchaseOrder).order_by(PurchaseOrder.purchase_id.desc()).all()]


@router.post("/purchases")
def create_purchase(data: PurchaseOrderCreate, db: Session = Depends(get_db)):
    total = sum(it.quantity * it.unit_price for it in data.items)
    po = PurchaseOrder(manufacturer_id=data.manufacturer_id, total_amount=total, status="PENDING")
    db.add(po); db.flush()
    for it in data.items:
        db.add(PurchaseDetail(purchase_id=po.purchase_id, product_id=it.product_id,
                              quantity=it.quantity, unit_price=it.unit_price, total_amount=it.quantity * it.unit_price))
    db.commit()
    log_op(db, 1, "管理员", "CREATE_PURCHASE", "purchase", po.purchase_id, f"总金额¥{total:.2f}")
    return {"message": "创建成功", "purchase_id": po.purchase_id}


@router.post("/purchases/{purchase_id}/confirm")
def confirm_purchase(purchase_id: int, db: Session = Depends(get_db)):
    po = db.query(PurchaseOrder).filter(PurchaseOrder.purchase_id == purchase_id).first()
    if not po or po.status != "PENDING": raise HTTPException(400, detail="状态异常")
    for d in db.query(PurchaseDetail).filter(PurchaseDetail.purchase_id == purchase_id).all():
        db.query(Product).filter(Product.product_id == d.product_id).update(
            {"stock_quantity": Product.stock_quantity + d.quantity})
        db.add(StockRecord(product_id=d.product_id, quantity_change=d.quantity, reason="PURCHASE",
                           related_id=purchase_id, operated_by=1))
    po.status = "COMPLETED"; db.commit()
    return {"message": "入库成功"}


@router.post("/purchases/from-low-stock")
def from_low_stock(data: dict, db: Session = Depends(get_db)):
    p = db.query(Product).filter(Product.product_id == data.get("product_id")).first()
    if not p: raise HTTPException(404, detail="商品不存在")
    sq = p.min_stock_threshold * 2 - p.stock_quantity
    if sq < 1: sq = p.min_stock_threshold
    return {"manufacturer_id": p.manufacturer_id, "product_id": p.product_id,
            "product_name": p.product_name, "suggest_quantity": sq,
            "suggest_unit_price": round(float(p.unit_price) * 0.7, 2)}


@router.get("/products")
def list_products_admin(db: Session = Depends(get_db)):
    return [{"product_id": p.product_id, "manufacturer_id": p.manufacturer_id,
             "manufacturer_name": (db.query(Manufacturer).filter(Manufacturer.manufacturer_id == p.manufacturer_id).first().manufacturer_name or "") if db.query(Manufacturer).filter(Manufacturer.manufacturer_id == p.manufacturer_id).first() else "",
             "product_name": p.product_name, "category": p.category,
             "unit_price": float(p.unit_price), "stock_quantity": p.stock_quantity,
             "min_stock_threshold": p.min_stock_threshold, "sales_count": p.sales_count,
             "description": p.description} for p in db.query(Product).all()]


@router.post("/products")
def add_product(data: dict, db: Session = Depends(get_db)):
    p = Product(manufacturer_id=data.get("manufacturer_id", 1), product_name=data.get("product_name", ""),
                category=data.get("category", ""), unit_price=data.get("unit_price", 0),
                stock_quantity=data.get("stock_quantity", 0), min_stock_threshold=data.get("min_stock_threshold", 10),
                description=data.get("description", ""))
    db.add(p); db.commit(); db.refresh(p)
    log_op(db, 1, "管理员", "ADD_PRODUCT", "product", p.product_id, f"添加：{p.product_name}")
    return {"message": "添加成功", "product_id": p.product_id}


@router.put("/products/{product_id}")
def update_product(product_id: int, data: dict, db: Session = Depends(get_db)):
    p = db.query(Product).filter(Product.product_id == product_id).first()
    if not p: raise HTTPException(404, detail="商品不存在")
    for k in ("product_name", "category", "unit_price", "stock_quantity", "min_stock_threshold", "description"):
        if k in data: setattr(p, k, data[k])
    db.commit()
    return {"message": "更新成功"}


@router.get("/reports/success-orders")
def report_success(db: Session = Depends(get_db)):
    return [{"order_id": o.order_id, "customer_name": (db.query(Customer).filter(Customer.customer_id == o.customer_id).first().customer_name or "") if db.query(Customer).filter(Customer.customer_id == o.customer_id).first() else "",
             "total_amount": float(o.total_amount), "status": o.status,
             "total_weight": float(o.total_weight) if o.total_weight else 0,
             "shipping_cost": float(o.shipping_cost) if o.shipping_cost else 0,
             "recipient_name": o.recipient_name, "recipient_address": o.recipient_address}
            for o in db.query(Order).filter(Order.status == "SHIPPED").all()]


@router.get("/reports/unpaid-orders")
def report_unpaid(db: Session = Depends(get_db)):
    return [{"order_id": o.order_id, "customer_name": (db.query(Customer).filter(Customer.customer_id == o.customer_id).first().customer_name or "") if db.query(Customer).filter(Customer.customer_id == o.customer_id).first() else "",
             "total_amount": float(o.total_amount), "status": o.status, "order_date": o.order_date}
            for o in db.query(Order).filter(Order.payment_status == 0).all()]


@router.get("/reports/unshipped-orders")
def report_unshipped(db: Session = Depends(get_db)):
    return [{"order_id": o.order_id, "customer_name": (db.query(Customer).filter(Customer.customer_id == o.customer_id).first().customer_name or "") if db.query(Customer).filter(Customer.customer_id == o.customer_id).first() else "",
             "total_amount": float(o.total_amount), "status": o.status,
             "total_weight": float(o.total_weight) if o.total_weight else 0}
            for o in db.query(Order).filter(Order.status.in_(["CONFIRMED", "OUT_OF_STOCK"])).all()]


@router.get("/reports/low-stock")
def report_low_stock(db: Session = Depends(get_db)):
    return [{"product_id": p.product_id, "product_name": p.product_name,
             "manufacturer_name": (db.query(Manufacturer).filter(Manufacturer.manufacturer_id == p.manufacturer_id).first().manufacturer_name or "") if db.query(Manufacturer).filter(Manufacturer.manufacturer_id == p.manufacturer_id).first() else "",
             "stock_quantity": p.stock_quantity, "min_stock_threshold": p.min_stock_threshold}
            for p in db.query(Product).filter(Product.stock_quantity < Product.min_stock_threshold).all()]


@router.get("/reports/stock-records", response_model=list[StockRecordResponse])
def report_stock_records(db: Session = Depends(get_db)):
    return db.query(StockRecord).order_by(StockRecord.operated_at.desc()).limit(100).all()


@router.get("/manufacturers")
def list_manufacturers(db: Session = Depends(get_db)):
    return db.query(Manufacturer).all()


@router.get("/operation-logs")
def list_logs(page: int = 1, page_size: int = 50, db: Session = Depends(get_db)):
    total = db.query(OperationLog).count()
    items = db.query(OperationLog).order_by(OperationLog.created_at.desc()).offset(
        (page - 1) * page_size).limit(page_size).all()
    return {"items": items, "total": total, "page": page, "page_size": page_size}
