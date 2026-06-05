from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models import Payment, Order, OrderDetail, Product, StockRecord
from schemas import PaymentCreate, PaymentResponse, RefundRequest
from abc import ABC, abstractmethod
import uuid

router = APIRouter(prefix="/api/payments", tags=["支付"])


class PaymentStrategy(ABC):
    @abstractmethod
    def pay(self, amount: float) -> dict:
        pass


class CreditCardPayment(PaymentStrategy):
    def pay(self, amount: float) -> dict:
        return {"method": "CREDIT_CARD", "transaction_id": f"CC-{uuid.uuid4().hex[:12]}", "message": f"信用卡支付 {amount} 元"}


class AlipayPayment(PaymentStrategy):
    def pay(self, amount: float) -> dict:
        return {"method": "ALIPAY", "transaction_id": f"ALI-{uuid.uuid4().hex[:12]}", "message": f"支付宝支付 {amount} 元"}


class WechatPayment(PaymentStrategy):
    def pay(self, amount: float) -> dict:
        return {"method": "WECHAT", "transaction_id": f"WX-{uuid.uuid4().hex[:12]}", "message": f"微信支付 {amount} 元"}


PAYMENT_STRATEGIES = {"CREDIT_CARD": CreditCardPayment(), "ALIPAY": AlipayPayment(), "WECHAT": WechatPayment()}


@router.post("/", response_model=PaymentResponse)
def create_payment(data: PaymentCreate, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.order_id == data.order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    strategy = PAYMENT_STRATEGIES.get(data.payment_method.upper())
    if not strategy:
        raise HTTPException(status_code=400, detail=f"不支持的支付方式: {data.payment_method}")
    result = strategy.pay(data.amount)
    payment = Payment(order_id=data.order_id, payment_method=result["method"], amount=data.amount,
                      transaction_id=result["transaction_id"], status="SUCCESS")
    db.add(payment)
    paid = db.query(func.sum(Payment.amount)).filter(Payment.order_id == data.order_id, Payment.status == "SUCCESS").scalar() or 0
    paid += data.amount
    if paid >= float(order.total_amount):
        order.payment_status = 1
    db.commit()
    db.refresh(payment)
    return payment


@router.post("/refund")
def refund(data: RefundRequest, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.order_id == data.order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    if order.status != "SHIPPED":
        raise HTTPException(status_code=400, detail="仅已发货订单可退款")
    order.status = "CANCELLED"
    details = db.query(OrderDetail).filter(OrderDetail.order_id == data.order_id).all()
    for d in details:
        db.query(Product).filter(Product.product_id == d.product_id).update(
            {"stock_quantity": Product.stock_quantity + d.quantity})
        db.add(StockRecord(product_id=d.product_id, quantity_change=d.quantity, reason="REFUND",
                           related_id=data.order_id, operated_by=1))
    refund_payment = Payment(order_id=data.order_id, payment_method="REFUND", amount=float(order.total_amount),
                             transaction_id=f"REF-{uuid.uuid4().hex[:12]}", status="SUCCESS")
    db.add(refund_payment)
    order.payment_status = 2
    db.commit()
    return {"message": "退款成功，库存已退回"}


@router.get("/order/{order_id}")
def get_order_payments(order_id: int, db: Session = Depends(get_db)):
    return db.query(Payment).filter(Payment.order_id == order_id).all()