from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Customer
from schemas import CustomerCreate, CustomerResponse, CustomerUpdate
import hashlib

router = APIRouter(prefix="/api/customers", tags=["顾客"])


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


@router.post("/register", response_model=CustomerResponse)
def register(data: CustomerCreate, db: Session = Depends(get_db)):
    exist = db.query(Customer).filter(Customer.username == data.username).first()
    if exist:
        raise HTTPException(status_code=400, detail="用户名已存在")
    customer = Customer(
        username=data.username,
        password=hash_password(data.password),
        customer_name=data.customer_name,
        address=data.address,
        postal_code=data.postal_code,
        phone=data.phone,
        email=data.email,
        role="customer",
    )
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


@router.post("/login")
def login(username: str, password: str, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.username == username).first()
    if not customer or customer.password != hash_password(password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    return {
        "customer_id": customer.customer_id,
        "customer_name": customer.customer_name,
        "role": customer.role,
        "message": "登录成功",
    }


@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="用户不存在")
    return customer


@router.put("/{customer_id}", response_model=CustomerResponse)
def update_customer(customer_id: int, data: CustomerUpdate, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="用户不存在")
    if data.customer_name is not None:
        customer.customer_name = data.customer_name
    if data.address is not None:
        customer.address = data.address
    if data.postal_code is not None:
        customer.postal_code = data.postal_code
    if data.phone is not None:
        customer.phone = data.phone
    if data.email is not None:
        customer.email = data.email
    db.commit()
    db.refresh(customer)
    return customer


@router.post("/forgot-password")
def forgot_password(username: str, email: str, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.username == username, Customer.email == email).first()
    if not customer:
        raise HTTPException(status_code=404, detail="用户名或邮箱不匹配")
    new_password = "reset123456"
    customer.password = hash_password(new_password)
    db.commit()
    return {"message": f"密码已重置为 {new_password}，请登录后修改"}