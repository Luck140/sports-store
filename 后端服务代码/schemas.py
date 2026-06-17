from pydantic import BaseModel, model_validator
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

    @model_validator(mode="before")
    @classmethod
    def empty_str_to_none(cls, values: dict) -> dict:
        """将空字符串转为None，避免写入数据库空值"""
        if not isinstance(values, dict):
            return values
        return {k: None if isinstance(v, str) and v == "" else v for k, v in values.items()}


class CustomerResponse(BaseModel):
    customer_id: int
    username: str
    customer_name: str
    role: str = "customer"
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    avatar: Optional[str] = None
    created_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class PasswordChange(BaseModel):
    old_password: str
    new_password: str


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
    invoice_address_phone: Optional[str] = None
    invoice_bank: Optional[str] = None


class OrderDetailResponse(BaseModel):
    detail_id: int
    order_id: int
    product_id: int
    product_name: str = ""
    product_name_snapshot: Optional[str] = None
    quantity: int
    unit_price: float
    total_amount: float
    model_config = {"from_attributes": True}


class PaymentCreate(BaseModel):
    order_id: int
    payment_method: str
    amount: float


class PurchaseDetailCreate(BaseModel):
    product_id: int
    quantity: int
    unit_price: float


class PurchaseOrderCreate(BaseModel):
    manufacturer_id: int
    items: list[PurchaseDetailCreate]


class StockRecordResponse(BaseModel):
    record_id: int
    product_id: int
    quantity_change: int
    reason: str
    related_id: Optional[int] = None
    operated_at: datetime
    model_config = {"from_attributes": True}


class AddressCreate(BaseModel):
    recipient_name: str
    phone: str
    address: str
    is_default: Optional[int] = 0
    tag: Optional[str] = None


class ReviewCreate(BaseModel):
    order_id: int
    product_id: int
    rating: int
    content: Optional[str] = None
    customer_id: Optional[int] = None


class ReviewResponse(BaseModel):
    review_id: int
    order_id: int
    product_id: int
    customer_id: int
    customer_name: str = ""
    rating: int
    content: Optional[str] = None
    created_at: datetime
    model_config = {"from_attributes": True}


class BannerResponse(BaseModel):
    banner_id: int
    title: str
    subtitle: Optional[str] = None
    image_url: Optional[str] = None
    link_type: str = "product"
    link_value: Optional[str] = None
    model_config = {"from_attributes": True}
