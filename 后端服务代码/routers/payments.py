from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Order, Payment, StockRecord, OrderDetail, Product, Notification
from schemas import PaymentCreate
from datetime import datetime
import uuid

router = APIRouter(prefix="/api/payments", tags=["支付"])


class _CC:
    def process(self, oid, amt): return {"transaction_id": f"CC-{uuid.uuid4().hex[:12].upper()}", "status": "SUCCESS"}


class _Ali:
    def process(self, oid, amt): return {"transaction_id": f"ALI-{uuid.uuid4().hex[:12].upper()}", "status": "SUCCESS"}


class _Wx:
    def process(self, oid, amt): return {"transaction_id": f"WX-{uuid.uuid4().hex[:12].upper()}", "status": "SUCCESS"}


_strats = {"credit_card": _CC(), "alipay": _Ali(), "wechat": _Wx()}


@router.post("/")
def create_payment(data: PaymentCreate, db: Session = Depends(get_db)):
    o = db.query(Order).filter(Order.order_id == data.order_id).first()
    if not o: raise HTTPException(404, detail="订单不存在")
    s = _strats.get(data.payment_method)
    if not s: raise HTTPException(400, detail=f"不支持的支付方式: {data.payment_method}")
    r = s.process(data.order_id, data.amount)
    p = Payment(order_id=data.order_id, payment_method=data.payment_method, amount=data.amount,
                transaction_id=r["transaction_id"], status=r["status"], payment_time=datetime.now())
    db.add(p)
    o.payment_status = 1
    db.commit()
    db.refresh(p)
    db.add(Notification(customer_id=o.customer_id, title="支付成功",
                        content=f"订单#{data.order_id}支付成功 ¥{data.amount:.2f}", notify_type="payment",
                        related_id=data.order_id))
    db.commit()
    return p


@router.get("/order/{order_id}")
def get_order_payments(order_id: int, db: Session = Depends(get_db)):
    return db.query(Payment).filter(Payment.order_id == order_id).order_by(Payment.payment_time.desc()).all()


@router.post("/refund/request")
def request_refund(data: dict, db: Session = Depends(get_db)):
    o = db.query(Order).filter(Order.order_id == data.get("order_id")).first()
    if not o or o.status != "SHIPPED" or o.payment_status != 1:
        raise HTTPException(400, detail="仅已发货已付款订单可申请退款")
    o.status = "REFUNDING"; db.commit()
    return {"message": "退款申请已提交"}


@router.post("/refund/approve")
def approve_refund(data: dict, db: Session = Depends(get_db)):
    o = db.query(Order).filter(Order.order_id == data.get("order_id")).first()
    if not o or o.status != "REFUNDING": raise HTTPException(400, detail="状态异常")
    for d in db.query(OrderDetail).filter(OrderDetail.order_id == o.order_id).all():
        db.query(Product).filter(Product.product_id == d.product_id).update(
            {"stock_quantity": Product.stock_quantity + d.quantity})
        db.add(StockRecord(product_id=d.product_id, quantity_change=d.quantity, reason="REFUND",
                           related_id=o.order_id, operated_by=1))
    o.status = "CANCELLED"; o.payment_status = 2; db.commit()
    db.add(Notification(customer_id=o.customer_id, title="退款成功",
                        content=f"订单#{o.order_id}已退款", notify_type="refund", related_id=o.order_id))
    db.commit()
    return {"message": "退款成功"}


@router.post("/refund/reject")
def reject_refund(data: dict, db: Session = Depends(get_db)):
    o = db.query(Order).filter(Order.order_id == data.get("order_id")).first()
    if not o or o.status != "REFUNDING": raise HTTPException(400, detail="状态异常")
    o.status = "SHIPPED"; db.commit()
    db.add(Notification(customer_id=o.customer_id, title="退款拒绝",
                        content=f"订单#{o.order_id}退款未通过", notify_type="refund", related_id=o.order_id))
    db.commit()
    return {"message": "已拒绝"}
