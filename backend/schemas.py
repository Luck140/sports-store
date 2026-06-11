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
    avatar: Optional[str] = None


class PasswordChange(BaseModel):
    old_password: str
    new_password: str


class CustomerResponse(BaseModel):
    customer_id: int
    username: str
    customer_name: str
    role: str = "customer"
    address: Optional[str] = None
    postal_code: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    avatar: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ProductResponse(BaseModel):
    product_id: int
    manufacturer_id: int
    product_name: str
    category: Optional[str] = "未分类"
    unit_price: float
    stock_quantity: int
    min_stock_threshold: int
    sales_count: int = 0
    description: Optional[str] = None

    class Config:
        from_attributes = True


class ProductDetailResponse(BaseModel):
    product_id: int
    manufacturer_id: int
    manufacturer_name: str = ""
    product_name: str
    category: Optional[str] = "未分类"
    unit_price: float
    stock_quantity: int
    min_stock_threshold: int
    sales_count: int = 0
    description: Optional[str] = None
    avg_rating: float = 0.0
    review_count: int = 0

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
    total_weight: Optional[float] = 0
    invoice_required: int = 0
    invoice_title: Optional[str] = None
    invoice_tax_no: Optional[str] = None
    address_id: Optional[int] = None


class OrderResponse(BaseModel):
    order_id: int
    customer_id: int
    order_date: datetime
    total_amount: float
    shipping_cost: Optional[float] = 0
    total_weight: Optional[float] = 0
    status: str
    payment_status: int
    recipient_name: Optional[str] = None
    recipient_address: Optional[str] = None
    recipient_phone: Optional[str] = None
    shipping_req: Optional[str] = None
    invoice_required: int = 0
    invoice_title: Optional[str] = None
    invoice_tax_no: Optional[str] = None

    class Config:
        from_attributes = True


class OrderDetailResponse(BaseModel):
    detail_id: int
    order_id: int
    product_id: int
    product_name: str = ""
    product_name_snapshot: Optional[str] = None
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
    payment_time: Optional[datetime] = None

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


class AddressCreate(BaseModel):
    recipient_name: str
    phone: str
    address: str
    is_default: Optional[int] = 0
    tag: Optional[str] = None


class AddressResponse(BaseModel):
    address_id: int
    customer_id: int
    recipient_name: str
    phone: str
    address: str
    is_default: int = 0
    tag: Optional[str] = None

    class Config:
        from_attributes = True


class ReviewCreate(BaseModel):
    order_id: int
    product_id: int
    rating: int
    content: Optional[str] = None


class ReviewResponse(BaseModel):
    review_id: int
    order_id: int
    product_id: int
    customer_id: int
    customer_name: str = ""
    rating: int
    content: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class BannerResponse(BaseModel):
    banner_id: int
    title: str
    subtitle: Optional[str] = None
    image_url: Optional[str] = None
    link_type: str = "product"
    link_value: Optional[str] = None

    class Config:
        from_attributes = True


class NotificationResponse(BaseModel):
    notify_id: int
    title: str
    content: Optional[str] = None
    notify_type: str
    related_id: Optional[int] = None
    is_read: int = 0
    created_at: datetime

    class Config:
        from_attributes = True
