# models.py - 数据库模型定义
from sqlalchemy import Column, BigInteger, String, Integer, Text, DECIMAL, Date, DateTime, ForeignKey, SmallInteger
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


class Customer(Base):
    __tablename__ = "customers"
    customer_id = Column(BigInteger, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    customer_name = Column(String(50), nullable=False)
    address = Column(String(255))
    postal_code = Column(String(20))
    phone = Column(String(255))
    email = Column(String(100))
    role = Column(String(20), nullable=False, default="customer")
    created_at = Column(DateTime, default=datetime.now)


class Manufacturer(Base):
    __tablename__ = "manufacturers"
    manufacturer_id = Column(BigInteger, primary_key=True, autoincrement=True)
    manufacturer_name = Column(String(100), nullable=False)
    contact_person = Column(String(50))
    contact_phone = Column(String(255))
    address = Column(String(255))


class Product(Base):
    __tablename__ = "products"
    product_id = Column(BigInteger, primary_key=True, autoincrement=True)
    manufacturer_id = Column(BigInteger, ForeignKey("manufacturers.manufacturer_id"), nullable=False)
    product_name = Column(String(200), nullable=False)
    unit_price = Column(DECIMAL(10, 2), nullable=False)
    stock_quantity = Column(Integer, nullable=False, default=0)
    min_stock_threshold = Column(Integer, nullable=False, default=10)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class Order(Base):
    __tablename__ = "orders"
    order_id = Column(BigInteger, primary_key=True, autoincrement=True)
    customer_id = Column(BigInteger, ForeignKey("customers.customer_id"), nullable=False)
    order_date = Column(DateTime, default=datetime.now)
    total_amount = Column(DECIMAL(12, 2), nullable=False, default=0.00)
    shipping_req = Column(String(100))
    shipping_date = Column(Date)
    total_weight = Column(DECIMAL(8, 2))
    shipping_cost = Column(DECIMAL(8, 2), default=0.00)
    payment_status = Column(SmallInteger, nullable=False, default=0)
    status = Column(String(20), nullable=False, default="PENDING")
    recipient_name = Column(String(50))
    recipient_address = Column(String(255))
    recipient_phone = Column(String(255))
    invoice_required = Column(SmallInteger, nullable=False, default=0)
    invoice_title = Column(String(200))
    invoice_tax_no = Column(String(50))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class OrderDetail(Base):
    __tablename__ = "order_details"
    detail_id = Column(BigInteger, primary_key=True, autoincrement=True)
    order_id = Column(BigInteger, ForeignKey("orders.order_id"), nullable=False)
    product_id = Column(BigInteger, ForeignKey("products.product_id"), nullable=False)
    manufacturer_id = Column(BigInteger, nullable=False, comment="下单时厂家快照")
    quantity = Column(Integer, nullable=False)
    unit_price = Column(DECIMAL(10, 2), nullable=False)
    total_amount = Column(DECIMAL(12, 2), nullable=False)


class Payment(Base):
    __tablename__ = "payments"
    payment_id = Column(BigInteger, primary_key=True, autoincrement=True)
    order_id = Column(BigInteger, ForeignKey("orders.order_id"), nullable=False)
    payment_method = Column(String(30), nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    payment_time = Column(DateTime, default=datetime.now)
    transaction_id = Column(String(100))
    status = Column(String(20), nullable=False, default="PENDING")


class StockRecord(Base):
    __tablename__ = "stock_records"
    record_id = Column(BigInteger, primary_key=True, autoincrement=True)
    product_id = Column(BigInteger, ForeignKey("products.product_id"), nullable=False)
    quantity_change = Column(Integer, nullable=False)
    reason = Column(String(50), nullable=False)
    related_id = Column(BigInteger)
    operated_by = Column(BigInteger)
    operated_at = Column(DateTime, default=datetime.now)


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"
    purchase_id = Column(BigInteger, primary_key=True, autoincrement=True)
    manufacturer_id = Column(BigInteger, ForeignKey("manufacturers.manufacturer_id"), nullable=False)
    purchase_date = Column(DateTime, default=datetime.now)
    total_amount = Column(DECIMAL(12, 2), nullable=False, default=0.00)
    status = Column(String(20), nullable=False, default="PENDING")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class PurchaseDetail(Base):
    __tablename__ = "purchase_details"
    detail_id = Column(BigInteger, primary_key=True, autoincrement=True)
    purchase_id = Column(BigInteger, ForeignKey("purchase_orders.purchase_id"), nullable=False)
    product_id = Column(BigInteger, ForeignKey("products.product_id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(DECIMAL(10, 2), nullable=False)
    total_amount = Column(DECIMAL(12, 2), nullable=False)