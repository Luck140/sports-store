from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models import (Order, OrderDetail, Product, StockRecord, Payment, PurchaseOrder,
                    PurchaseDetail, Manufacturer, Customer, Review, OperationLog, Notification)
from schemas import PurchaseOrderCreate, StockRecordResponse
from datetime import datetime
import redis

router = APIRouter(prefix="/api/admin", tags=["管理员"])
redis_client = redis.StrictRedis(host="localhost", port=6379, db=0, charset="utf-8", decode_responses=True)


def log_operation(db, operator_id, operator_name, operation_type, target_type, target_id, detail=""):
    db.add(OperationLog(operator_id=operator_id, operator_name=operator_name,
                         operation_type=operation_type, target_type=target_type,
                         target_id=target_id, detail=detail))
    db.commit()


def add_notification(db, customer_id, title, content, notify_type, related_id=None):
    db.add(Notification(customer_id=customer_id, title=title, content=content,
                         notify_type=notify_type, related_id=related_id))
    db.commit()


# ========== 仪表盘 ==========
@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db)):
    pending_count = db.query(Order).filter(Order.status == "PENDING").count()
    refunding_count = db.query(Order).filter(Order.status == "REFUNDING").count()
    low_stock_count = db.query(Product).filter(Product.stock_quantity < Product.min_stock_threshold).count()
    today_orders = db.query(Order).filter(func.date(Order.order_date) == func.current_date()).count()
    return {
        "total_orders": db.query(Order).count(),
        "pending_orders": pending_count,
        "unshipped_orders": db.query(Order).filter(Order.status.in_(["CONFIRMED", "OUT_OF_STOCK"])).count(),
        "low_stock_count": low_stock_count,
        "refunding_count": refunding_count,
        "today_orders": today_orders,
        "pending_todos": [
            {"type": "order", "count": pending_count, "label": "待确认订单", "link": "/admin/orders?status=PENDING"},
            {"type": "stock", "count": low_stock_count, "label": "库存预警商品", "link": "/admin/reports?type=lowstock"},
            {"type": "refund", "count": refunding_count, "label": "待审核退款", "link": "/admin/orders?status=REFUNDING"},
        ],
    }


# ========== 销售图表数据 ==========
@router.get("/dashboard/sales-chart")
def sales_chart(db: Session = Depends(get_db)):
    from sqlalchemy import extract
    results = db.query(
        func.date_format(Order.order_date, "%Y-%m-%d").label("day"),
        func.count(Order.order_id).label("count"),
        func.coalesce(func.sum(Order.total_amount), 0).label("amount")
    ).filter(Order.status.in_(["CONFIRMED", "SHIPPED", "COMPLETED"])).group_by("day").order_by(func.date(Order.order_date).desc()).limit(30).all()
    return [{"date": r.day, "count": r.count, "amount": float(r.amount)} for r in results]


@router.get("/dashboard/hot-products")
def hot_products(db: Session = Depends(get_db)):
    products = db.query(Product).order_by(Product.sales_count.desc()).limit(5).all()
    return [{"product_id": p.product_id, "product_name": p.product_name, "sales_count": p.sales_count} for p in products]


# ========== 订单管理 ==========
@router.post("/orders/{order_id}/confirm")
def confirm_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    if order.status != "PENDING":
        raise HTTPException(status_code=400, detail="仅待确认订单可确认")
    lock = redis_client.lock(f"lock:order:{order_id}", timeout=10)
    acquired = lock.acquire(blocking=True, blocking_timeout=5)
    if not acquired:
        raise HTTPException(status_code=409, detail="订单处理中")
    try:
        details = db.query(OrderDetail).filter(OrderDetail.order_id == order_id).all()
        for d in details:
            product = db.query(Product).filter(Product.product_id == d.product_id).first()
            if not product or product.stock_quantity < d.quantity:
                order.status = "OUT_OF_STOCK"
                db.commit()
                log_operation(db, 1, "管理员", "CONFIRM_ORDER", "order", order_id, "确认失败：库存不足")
                add_notification(db, order.customer_id, "订单库存不足",
                                 f"您的订单 #{order_id} 因库存不足暂时无法发货。", "order_status", order_id)
                return {"message": f"商品 {d.product_id} 库存不足", "status": "OUT_OF_STOCK"}
        for d in details:
            db.query(Product).filter(Product.product_id == d.product_id, Product.stock_quantity >= d.quantity).update(
                {"stock_quantity": Product.stock_quantity - d.quantity})
            db.add(StockRecord(product_id=d.product_id, quantity_change=-d.quantity, reason="ORDER_CONFIRM",
                               related_id=order_id, operated_by=1))
        order.status = "CONFIRMED"
        db.commit()
        log_operation(db, 1, "管理员", "CONFIRM_ORDER", "order", order_id, "订单确认成功")
        add_notification(db, order.customer_id, "订单已确认",
                         f"您的订单 #{order_id} 已确认，正在备货中。", "order_status", order_id)
        return {"message": "订单确认成功", "status": "CONFIRMED"}
    finally:
        lock.release()


@router.post("/orders/{order_id}/ship")
def ship_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order or order.status != "CONFIRMED":
        raise HTTPException(status_code=400, detail="仅已确认订单可发货")
    if order.total_weight and float(order.total_weight) > 0:
        order.shipping_cost = float(order.total_weight) * 10
    order.status = "SHIPPED"
    order.shipping_date = datetime.now()
    db.commit()
    log_operation(db, 1, "管理员", "SHIP_ORDER", "order", order_id,
                  f"发货成功，运费 ¥{float(order.shipping_cost):.2f}")
    add_notification(db, order.customer_id, "订单已发货",
                     f"您的订单 #{order_id} 已发货，请注意查收。", "order_status", order_id)
    return {"message": "发货成功", "shipping_cost": float(order.shipping_cost) if order.shipping_cost else 0}


@router.post("/orders/{order_id}/cancel")
def cancel_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    if order.status == "SHIPPED":
        raise HTTPException(status_code=400, detail="已发货订单不支持取消")
    if order.status == "CANCELLED":
        raise HTTPException(status_code=400, detail="订单已取消")
    if order.status == "CONFIRMED":
        details = db.query(OrderDetail).filter(OrderDetail.order_id == order_id).all()
        for d in details:
            db.query(Product).filter(Product.product_id == d.product_id).update(
                {"stock_quantity": Product.stock_quantity + d.quantity})
            db.add(StockRecord(product_id=d.product_id, quantity_change=d.quantity, reason="ORDER_CANCEL",
                               related_id=order_id, operated_by=1))
    order.status = "CANCELLED"
    db.commit()
    log_operation(db, 1, "管理员", "CANCEL_ORDER", "order", order_id, "管理员取消订单")
    add_notification(db, order.customer_id, "订单已取消",
                     f"您的订单 #{order_id} 已被管理员取消。", "order_status", order_id)
    return {"message": "订单已取消"}


# 批量确认
@router.post("/orders/batch-confirm")
def batch_confirm(data: dict, db: Session = Depends(get_db)):
    order_ids = data.get("order_ids", [])
    results = []
    for oid in order_ids:
        try:
            confirm_order(oid, db)
            results.append({"order_id": oid, "status": "success"})
        except HTTPException as e:
            results.append({"order_id": oid, "status": "failed", "detail": e.detail})
    return {"results": results}


# 批量发货
@router.post("/orders/batch-ship")
def batch_ship(data: dict, db: Session = Depends(get_db)):
    order_ids = data.get("order_ids", [])
    results = []
    for oid in order_ids:
        try:
            ship_order(oid, db)
            results.append({"order_id": oid, "status": "success"})
        except HTTPException as e:
            results.append({"order_id": oid, "status": "failed", "detail": e.detail})
    return {"results": results}


@router.get("/orders")
def list_all_orders(
    status: str = Query(None), keyword: str = Query(None),
    page: int = Query(1), page_size: int = Query(20),
    db: Session = Depends(get_db),
):
    q = db.query(Order)
    if status:
        q = q.filter(Order.status == status)
    if keyword:
        q2 = db.query(Customer).filter(Customer.customer_name.contains(keyword)).all()
        cids = [c.customer_id for c in q2]
        try:
            oid = int(keyword)
            q = q.filter((Order.order_id == oid) | (Order.customer_id.in_(cids)) if cids else (Order.order_id == oid))
        except ValueError:
            if cids:
                q = q.filter(Order.customer_id.in_(cids))
    total = q.count()
    total_pages = max(1, (total + page_size - 1) // page_size)
    orders = q.order_by(Order.order_id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    result = []
    for o in orders:
        customer = db.query(Customer).filter(Customer.customer_id == o.customer_id).first()
        result.append({
            "order_id": o.order_id, "customer_id": o.customer_id,
            "customer_name": customer.customer_name if customer else "",
            "customer_phone": customer.phone if customer else "",
            "total_amount": float(o.total_amount), "status": o.status,
            "payment_status": o.payment_status, "shipping_req": o.shipping_req,
            "recipient_name": o.recipient_name, "recipient_address": o.recipient_address,
            "recipient_phone": o.recipient_phone,
            "total_weight": float(o.total_weight) if o.total_weight else 0,
            "shipping_cost": float(o.shipping_cost) if o.shipping_cost else 0,
            "invoice_required": o.invoice_required, "invoice_title": o.invoice_title,
            "invoice_tax_no": o.invoice_tax_no,
            "order_date": o.order_date,
        })
    return {"items": result, "total": total, "page": page, "page_size": page_size,
            "total_pages": total_pages, "has_next": page < total_pages, "has_prev": page > 1}


# 顾客详情
@router.get("/customers/{customer_id}")
def get_customer_detail(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="顾客不存在")
    orders = db.query(Order).filter(Order.customer_id == customer_id).order_by(Order.order_id.desc()).limit(20).all()
    total_spent = db.query(func.coalesce(func.sum(Order.total_amount), 0)).filter(
        Order.customer_id == customer_id, Order.payment_status.in_([1, 2])
    ).scalar()
    return {
        "customer_id": customer.customer_id, "customer_name": customer.customer_name,
        "username": customer.username, "phone": customer.phone, "email": customer.email,
        "address": customer.address, "created_at": customer.created_at,
        "total_orders": len(orders),
        "total_spent": float(total_spent),
    }


# ========== 进货管理 ==========
@router.get("/purchases")
def list_purchases(db: Session = Depends(get_db)):
    purchases = db.query(PurchaseOrder).order_by(PurchaseOrder.purchase_id.desc()).all()
    result = []
    for p in purchases:
        mfr = db.query(Manufacturer).filter(Manufacturer.manufacturer_id == p.manufacturer_id).first()
        result.append({
            "purchase_id": p.purchase_id, "manufacturer_id": p.manufacturer_id,
            "manufacturer_name": mfr.manufacturer_name if mfr else "",
            "total_amount": float(p.total_amount), "status": p.status,
        })
    return result


@router.post("/purchases")
def create_purchase(data: PurchaseOrderCreate, db: Session = Depends(get_db)):
    total = 0.0
    for item in data.items:
        total += item.quantity * item.unit_price
    po = PurchaseOrder(manufacturer_id=data.manufacturer_id, total_amount=total, status="PENDING")
    db.add(po)
    db.flush()
    for item in data.items:
        db.add(PurchaseDetail(purchase_id=po.purchase_id, product_id=item.product_id,
                              quantity=item.quantity, unit_price=item.unit_price,
                              total_amount=item.quantity * item.unit_price))
    db.commit()
    log_operation(db, 1, "管理员", "CREATE_PURCHASE", "purchase", po.purchase_id,
                  f"创建进货单，总金额 ¥{total:.2f}")
    return {"message": "进货单创建成功", "purchase_id": po.purchase_id}


@router.post("/purchases/{purchase_id}/confirm")
def confirm_purchase(purchase_id: int, db: Session = Depends(get_db)):
    po = db.query(PurchaseOrder).filter(PurchaseOrder.purchase_id == purchase_id).first()
    if not po or po.status != "PENDING":
        raise HTTPException(status_code=400, detail="进货单状态异常")
    details = db.query(PurchaseDetail).filter(PurchaseDetail.purchase_id == purchase_id).all()
    for d in details:
        db.query(Product).filter(Product.product_id == d.product_id).update(
            {"stock_quantity": Product.stock_quantity + d.quantity})
        db.add(StockRecord(product_id=d.product_id, quantity_change=d.quantity, reason="PURCHASE",
                           related_id=purchase_id, operated_by=1))
    po.status = "COMPLETED"
    db.commit()
    log_operation(db, 1, "管理员", "CONFIRM_PURCHASE", "purchase", purchase_id, "进货入库成功")
    return {"message": "入库成功"}


# 从库存预警一键生成进货单
@router.post("/purchases/from-low-stock")
def create_purchase_from_low_stock(data: dict, db: Session = Depends(get_db)):
    product_id = data.get("product_id")
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    suggest_qty = product.min_stock_threshold * 2 - product.stock_quantity
    if suggest_qty < 1:
        suggest_qty = product.min_stock_threshold
    return {
        "manufacturer_id": product.manufacturer_id,
        "product_id": product.product_id,
        "product_name": product.product_name,
        "suggest_quantity": suggest_qty,
        "suggest_unit_price": float(product.unit_price) * 0.7,
    }


# ========== 商品管理 ==========
@router.get("/products")
def list_products(db: Session = Depends(get_db)):
    products = db.query(Product).all()
    result = []
    for p in products:
        mfr = db.query(Manufacturer).filter(Manufacturer.manufacturer_id == p.manufacturer_id).first()
        result.append({
            "product_id": p.product_id, "manufacturer_id": p.manufacturer_id,
            "manufacturer_name": mfr.manufacturer_name if mfr else "",
            "product_name": p.product_name, "category": p.category,
            "unit_price": float(p.unit_price), "stock_quantity": p.stock_quantity,
            "min_stock_threshold": p.min_stock_threshold, "sales_count": p.sales_count,
            "description": p.description,
        })
    return result


@router.post("/products")
def add_product(data: dict, db: Session = Depends(get_db)):
    product = Product(
        manufacturer_id=data.get("manufacturer_id", 1),
        product_name=data.get("product_name", ""),
        category=data.get("category", "未分类"),
        unit_price=data.get("unit_price", 0),
        stock_quantity=data.get("stock_quantity", 0),
        min_stock_threshold=data.get("min_stock_threshold", 10),
        description=data.get("description", ""),
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    log_operation(db, 1, "管理员", "ADD_PRODUCT", "product", product.product_id,
                  f"添加商品：{product.product_name}")
    return {"message": "商品添加成功", "product_id": product.product_id}


@router.put("/products/{product_id}")
def update_product(product_id: int, data: dict, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    if "product_name" in data: product.product_name = data["product_name"]
    if "category" in data: product.category = data["category"]
    if "unit_price" in data: product.unit_price = data["unit_price"]
    if "stock_quantity" in data: product.stock_quantity = data["stock_quantity"]
    if "min_stock_threshold" in data: product.min_stock_threshold = data["min_stock_threshold"]
    if "description" in data: product.description = data["description"]
    db.commit()
    return {"message": "商品更新成功"}


# ========== 报表 ==========
@router.get("/reports/success-orders")
def report_success_orders(db: Session = Depends(get_db)):
    orders = db.query(Order).filter(Order.status == "SHIPPED").all()
    result = []
    for o in orders:
        customer = db.query(Customer).filter(Customer.customer_id == o.customer_id).first()
        result.append({
            "order_id": o.order_id, "customer_name": customer.customer_name if customer else "",
            "total_amount": float(o.total_amount), "status": o.status,
            "total_weight": float(o.total_weight) if o.total_weight else 0,
            "shipping_cost": float(o.shipping_cost) if o.shipping_cost else 0,
            "recipient_name": o.recipient_name, "recipient_address": o.recipient_address,
        })
    return result


@router.get("/reports/unpaid-orders")
def report_unpaid_orders(db: Session = Depends(get_db)):
    orders = db.query(Order).filter(Order.payment_status == 0).all()
    result = []
    for o in orders:
        customer = db.query(Customer).filter(Customer.customer_id == o.customer_id).first()
        result.append({
            "order_id": o.order_id, "customer_name": customer.customer_name if customer else "",
            "total_amount": float(o.total_amount), "status": o.status, "order_date": o.order_date,
        })
    return result


@router.get("/reports/unshipped-orders")
def report_unshipped_orders(db: Session = Depends(get_db)):
    orders = db.query(Order).filter(Order.status.in_(["CONFIRMED", "OUT_OF_STOCK"])).all()
    result = []
    for o in orders:
        customer = db.query(Customer).filter(Customer.customer_id == o.customer_id).first()
        result.append({
            "order_id": o.order_id, "customer_name": customer.customer_name if customer else "",
            "total_amount": float(o.total_amount), "status": o.status,
            "total_weight": float(o.total_weight) if o.total_weight else 0,
        })
    return result


@router.get("/reports/low-stock")
def report_low_stock(db: Session = Depends(get_db)):
    products = db.query(Product).filter(Product.stock_quantity < Product.min_stock_threshold).all()
    result = []
    for p in products:
        mfr = db.query(Manufacturer).filter(Manufacturer.manufacturer_id == p.manufacturer_id).first()
        result.append({
            "product_id": p.product_id, "product_name": p.product_name,
            "manufacturer_name": mfr.manufacturer_name if mfr else "",
            "manufacturer_id": p.manufacturer_id,
            "stock_quantity": p.stock_quantity, "min_stock_threshold": p.min_stock_threshold,
        })
    return result


@router.get("/reports/stock-records", response_model=list[StockRecordResponse])
def report_stock_records(db: Session = Depends(get_db)):
    return db.query(StockRecord).order_by(StockRecord.operated_at.desc()).limit(100).all()


@router.get("/manufacturers")
def list_manufacturers(db: Session = Depends(get_db)):
    return db.query(Manufacturer).all()


# ========== 操作日志 ==========
@router.get("/operation-logs")
def list_operation_logs(page: int = Query(1), page_size: int = Query(50), db: Session = Depends(get_db)):
    total = db.query(OperationLog).count()
    logs = db.query(OperationLog).order_by(OperationLog.created_at.desc()).offset(
        (page - 1) * page_size).limit(page_size).all()
    return {"items": logs, "total": total, "page": page, "page_size": page_size}
