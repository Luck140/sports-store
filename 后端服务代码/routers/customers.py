from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Customer, Address, Favorite, Product
from schemas import CustomerCreate, CustomerResponse, CustomerUpdate, PasswordChange, AddressCreate
import hashlib

router = APIRouter(prefix="/api/customers", tags=["顾客"])


def hp(p: str) -> str:
    return hashlib.sha256(p.encode()).hexdigest()


@router.post("/register", response_model=CustomerResponse)
def register(data: CustomerCreate, db: Session = Depends(get_db)):
    if db.query(Customer).filter(Customer.username == data.username).first():
        raise HTTPException(400, detail="用户名已存在")
    c = Customer(username=data.username, password=hp(data.password),
                 customer_name=data.customer_name, address=data.address,
                 phone=data.phone, email=data.email, role="customer")
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


@router.post("/login")
def login(username: str, password: str, db: Session = Depends(get_db)):
    c = db.query(Customer).filter(Customer.username == username).first()
    if not c or c.password != hp(password):
        raise HTTPException(401, detail="用户名或密码错误")
    return {"customer_id": c.customer_id, "username": c.username,
            "customer_name": c.customer_name, "role": c.role, "message": "登录成功"}


@router.get("/{customer_id}")
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    c = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if not c: raise HTTPException(404, detail="用户不存在")
    return c


@router.put("/{customer_id}")
def update_customer(customer_id: int, data: CustomerUpdate, db: Session = Depends(get_db)):
    c = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if not c: raise HTTPException(404, detail="用户不存在")
    # 只更新有值的字段（排除 None 和空字符串）
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(c, k, v)
    db.commit()
    db.refresh(c)
    return c


@router.post("/{customer_id}/change-password")
def change_password(customer_id: int, data: PasswordChange, db: Session = Depends(get_db)):
    c = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if not c or c.password != hp(data.old_password):
        raise HTTPException(400, detail="原密码错误")
    if len(data.new_password) < 6: raise HTTPException(400, detail="新密码至少6位")
    c.password = hp(data.new_password)
    db.commit()
    return {"message": "密码修改成功"}


@router.post("/forgot-password")
def forgot_password(username: str, email: str, db: Session = Depends(get_db)):
    c = db.query(Customer).filter(Customer.username == username, Customer.email == email).first()
    if not c: raise HTTPException(404, detail="用户名或邮箱不匹配")
    c.password = hp("reset123456")
    db.commit()
    return {"message": "密码已重置为 reset123456，请登录后修改"}


@router.get("/{customer_id}/addresses")
def list_addresses(customer_id: int, db: Session = Depends(get_db)):
    return db.query(Address).filter(Address.customer_id == customer_id)\
        .order_by(Address.is_default.desc(), Address.address_id.desc()).all()


@router.post("/{customer_id}/addresses")
def add_address(customer_id: int, data: AddressCreate, db: Session = Depends(get_db)):
    if data.is_default:
        db.query(Address).filter(Address.customer_id == customer_id).update({"is_default": 0})
    a = Address(customer_id=customer_id, **data.model_dump())
    db.add(a); db.commit(); db.refresh(a)
    return a


@router.put("/{customer_id}/addresses/{address_id}")
def update_address(customer_id: int, address_id: int, data: AddressCreate, db: Session = Depends(get_db)):
    a = db.query(Address).filter(Address.address_id == address_id, Address.customer_id == customer_id).first()
    if not a: raise HTTPException(404, detail="地址不存在")
    if data.is_default:
        db.query(Address).filter(Address.customer_id == customer_id).update({"is_default": 0})
    for k, v in data.model_dump().items(): setattr(a, k, v)
    db.commit(); db.refresh(a)
    return a


@router.delete("/{customer_id}/addresses/{address_id}")
def delete_address(customer_id: int, address_id: int, db: Session = Depends(get_db)):
    a = db.query(Address).filter(Address.address_id == address_id, Address.customer_id == customer_id).first()
    if not a: raise HTTPException(404, detail="地址不存在")
    db.delete(a); db.commit()
    return {"message": "已删除"}


@router.get("/{customer_id}/favorites")
def list_favorites(customer_id: int, db: Session = Depends(get_db)):
    items = []
    for f in db.query(Favorite).filter(Favorite.customer_id == customer_id).order_by(Favorite.created_at.desc()).all():
        p = db.query(Product).filter(Product.product_id == f.product_id).first()
        if p: items.append({"favorite_id": f.favorite_id, "product_id": p.product_id,
                            "product_name": p.product_name, "unit_price": float(p.unit_price), "category": p.category})
    return items


@router.post("/{customer_id}/favorites/{product_id}")
def add_favorite(customer_id: int, product_id: int, db: Session = Depends(get_db)):
    if db.query(Favorite).filter(Favorite.customer_id == customer_id, Favorite.product_id == product_id).first():
        raise HTTPException(400, detail="已收藏")
    db.add(Favorite(customer_id=customer_id, product_id=product_id)); db.commit()
    return {"message": "收藏成功"}


@router.delete("/{customer_id}/favorites/{product_id}")
def remove_favorite(customer_id: int, product_id: int, db: Session = Depends(get_db)):
    f = db.query(Favorite).filter(Favorite.customer_id == customer_id, Favorite.product_id == product_id).first()
    if not f: raise HTTPException(404, detail="未收藏")
    db.delete(f); db.commit()
    return {"message": "已取消收藏"}
