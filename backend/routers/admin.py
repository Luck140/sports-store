from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Order, OrderDetail, Product, StockRecord, Payment, PurchaseOrder, PurchaseDetail, Manufacturer, Customer
from schemas import PurchaseOrderCreate, StockRecordResponse
import redis

router = APIRouter(prefix="/api/admin", tags=["管理员"])
redis_client = redis.StrictRedis(host="localhost", port=6379, db=0, charset="utf-8", decode_responses=True)


# ========== 仪表盘 ==========
@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db)):
    return {
        "total_orders": db.query(Order).count(),
        "pending_orders": db.query(Order).filter(Order.status == "PENDING").count(),
        "unshipped_orders": db.query(Order).filter(Order.status.in_(["CONFIRMED", "OUT_OF_STOCK"])).count(),
        "low_stock_count": db.query(Product).filter(Product.stock_quantity < Product.min_stock_threshold).count(),
    }


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
                return {"message": f"商品 {d.product_id} 库存不足", "status": "OUT_OF_STOCK"}
        for d in details:
            db.query(Product).filter(Product.product_id == d.product_id, Product.stock_quantity >= d.quantity).update(
                {"stock_quantity": Product.stock_quantity - d.quantity})
            db.add(StockRecord(product_id=d.product_id, quantity_change=-d.quantity, reason="ORDER_CONFIRM",
                               related_id=order_id, operated_by=1))
        order.status = "CONFIRMED"
        db.commit()
        return {"message": "订单确认成功，库存已扣减", "status": "CONFIRMED"}
    finally:
        lock.release()


@router.post("/orders/{order_id}/ship")
def ship_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order or order.status != "CONFIRMED":
        raise HTTPException(status_code=400, detail="仅已确认订单可发货")
    # 发货时自动计算运费（按重量*10元/kg估算）
    if order.total_weight and float(order.total_weight) > 0:
        order.shipping_cost = float(order.total_weight) * 10
    order.status = "SHIPPED"
    db.commit()
    return {"message": "发货成功"}


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
    return {"message": "订单已取消"}


@router.get("/orders")
def list_all_orders(db: Session = Depends(get_db)):
    orders = db.query(Order).order_by(Order.order_id.desc()).all()
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
        })
    return result


# ========== 进货管理 ==========
@router.get("/purchases")
def list_purchases(db: Session = Depends(get_db)):
    purchases = db.query(PurchaseOrder).order_by(PurchaseOrder.purchase_id.desc()).all()
    result = []
    for p in purchases:
        mfr = db.query(Manufacturer).filter(Manufacturer.manufacturer_id == p.manufacturer_id).first()
        result.append({
            "purchase_id": p.purchase_id,
            "manufacturer_id": p.manufacturer_id,
            "manufacturer_name": mfr.manufacturer_name if mfr else "",
            "total_amount": float(p.total_amount),
            "status": p.status,
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
    return {"message": "入库成功"}


# ========== 商品管理 ==========
@router.get("/products")
def list_products(db: Session = Depends(get_db)):
    products = db.query(Product).all()
    result = []
    for p in products:
        mfr = db.query(Manufacturer).filter(Manufacturer.manufacturer_id == p.manufacturer_id).first()
        result.append({
            "product_id": p.product_id,
            "manufacturer_id": p.manufacturer_id,
            "manufacturer_name": mfr.manufacturer_name if mfr else "",
            "product_name": p.product_name,
            "unit_price": float(p.unit_price),
            "stock_quantity": p.stock_quantity,
            "min_stock_threshold": p.min_stock_threshold,
            "description": p.description,
        })
    return result


@router.post("/products")
def add_product(data: dict, db: Session = Depends(get_db)):
    product = Product(
        manufacturer_id=data.get("manufacturer_id", 1),
        product_name=data.get("product_name", ""),
        unit_price=data.get("unit_price", 0),
        stock_quantity=data.get("stock_quantity", 0),
        min_stock_threshold=data.get("min_stock_threshold", 10),
        description=data.get("description", ""),
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return {"message": "商品添加成功", "product_id": product.product_id}


@router.put("/products/{product_id}")
def update_product(product_id: int, data: dict, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    if "product_name" in data: product.product_name = data["product_name"]
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
            "total_amount": float(o.total_amount), "status": o.status,
            "order_date": o.order_date,
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
            "stock_quantity": p.stock_quantity, "min_stock_threshold": p.min_stock_threshold,
        })
    return result


@router.get("/reports/stock-records", response_model=list[StockRecordResponse])
def report_stock_records(db: Session = Depends(get_db)):
    return db.query(StockRecord).order_by(StockRecord.operated_at.desc()).limit(100).all()


@router.get("/manufacturers")
def list_manufacturers(db: Session = Depends(get_db)):
    return db.query(Manufacturer).all()