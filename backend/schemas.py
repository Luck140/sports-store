from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CustomerCreate(BaseModel):
    username: str
    password: str
    customer_name: str
    address: Optional[str] = None
    postal_code: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None


class CustomerUpdate(BaseModel):
    customer_name: Optional[str] = None
    address: Optional[str] = None
    postal_code: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None


class CustomerResponse(BaseModel):
    customer_id: int
    username: str
    customer_name: str
    role: str = "customer"
    address: Optional[str] = None
    postal_code: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None

    class Config:
        from_attributes = True


class ProductResponse(BaseModel):
    product_id: int
    manufacturer_id: int
    product_name: str
    unit_price: float
    stock_quantity: int
    min_stock_threshold: int
    description: Optional[str] = None

    class Config:
        from_attributes = True


class ProductDetailResponse(BaseModel):
    product_id: int
    manufacturer_id: int
    manufacturer_name: str = ""
    product_name: str
    unit_price: float
    stock_quantity: int
    min_stock_threshold: int
    description: Optional[str] = None

    class Config:
        from_attributes = True


class OrderDetailCreate(BaseModel):
    product_id: int
    manufacturer_id: int
    quantity: int
    unit_price: float


class OrderCreate(BaseModel):
    customer_id: int
    items: list[OrderDetailCreate]
    shipping_req: Optional[str] = None
    recipient_name: Optional[str] = None
    recipient_address: Optional[str] = None
    recipient_phone: Optional[str] = None
    invoice_required: int = 0
    invoice_title: Optional[str] = None
    invoice_tax_no: Optional[str] = None


class OrderResponse(BaseModel):
    order_id: int
    customer_id: int
    order_date: datetime
    total_amount: float
    status: str
    payment_status: int
    recipient_name: Optional[str] = None
    recipient_address: Optional[str] = None
    recipient_phone: Optional[str] = None

    class Config:
        from_attributes = True


class OrderDetailResponse(BaseModel):
    detail_id: int
    order_id: int
    product_id: int
    product_name: str = ""
    quantity: int
    unit_price: float
    total_amount: float

    class Config:
        from_attributes = True


class PaymentCreate(BaseModel):
    order_id: int
    payment_method: str
    amount: float


class PaymentResponse(BaseModel):
    payment_id: int
    order_id: int
    payment_method: str
    amount: float
    status: str
    transaction_id: Optional[str] = None

    class Config:
        from_attributes = True


class PurchaseDetailCreate(BaseModel):
    product_id: int
    quantity: int
    unit_price: float


class PurchaseOrderCreate(BaseModel):
    manufacturer_id: int
    items: list[PurchaseDetailCreate]


class PurchaseOrderResponse(BaseModel):
    purchase_id: int
    manufacturer_id: int
    total_amount: float
    status: str

    class Config:
        from_attributes = True


class StockRecordResponse(BaseModel):
    record_id: int
    product_id: int
    quantity_change: int
    reason: str
    related_id: Optional[int] = None
    operated_at: datetime

    class Config:
        from_attributes = True


class RefundRequest(BaseModel):
    order_id: int
    reason: str