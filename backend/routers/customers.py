from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Customer, Address, Favorite, Product
from schemas import CustomerCreate, CustomerResponse, CustomerUpdate, PasswordChange, AddressCreate, AddressResponse
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
        username=data.username, password=hash_password(data.password),
        customer_name=data.customer_name, address=data.address,
        postal_code=data.postal_code, phone=data.phone, email=data.email, role="customer",
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
        "customer_id": customer.customer_id, "customer_name": customer.customer_name,
        "role": customer.role, "message": "登录成功",
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
    if data.customer_name is not None: customer.customer_name = data.customer_name
    if data.address is not None: customer.address = data.address
    if data.postal_code is not None: customer.postal_code = data.postal_code
    if data.phone is not None: customer.phone = data.phone
    if data.email is not None: customer.email = data.email
    if data.avatar is not None: customer.avatar = data.avatar
    db.commit()
    db.refresh(customer)
    return customer


@router.post("/{customer_id}/change-password")
def change_password(customer_id: int, data: PasswordChange, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="用户不存在")
    if customer.password != hash_password(data.old_password):
        raise HTTPException(status_code=400, detail="原密码错误")
    if len(data.new_password) < 6:
        raise HTTPException(status_code=400, detail="新密码至少6位")
    customer.password = hash_password(data.new_password)
    db.commit()
    return {"message": "密码修改成功"}


@router.post("/forgot-password")
def forgot_password(username: str, email: str, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.username == username, Customer.email == email).first()
    if not customer:
        raise HTTPException(status_code=404, detail="用户名或邮箱不匹配")
    new_password = "reset123456"
    customer.password = hash_password(new_password)
    db.commit()
    return {"message": f"密码已重置为 {new_password}，请登录后修改"}


# ========== 地址管理 ==========
@router.get("/{customer_id}/addresses", response_model=list[AddressResponse])
def list_addresses(customer_id: int, db: Session = Depends(get_db)):
    return db.query(Address).filter(Address.customer_id == customer_id).order_by(Address.is_default.desc(), Address.address_id.desc()).all()


@router.post("/{customer_id}/addresses", response_model=AddressResponse)
def add_address(customer_id: int, data: AddressCreate, db: Session = Depends(get_db)):
    if data.is_default:
        db.query(Address).filter(Address.customer_id == customer_id).update({"is_default": 0})
    addr = Address(customer_id=customer_id, recipient_name=data.recipient_name,
                   phone=data.phone, address=data.address,
                   is_default=data.is_default, tag=data.tag)
    db.add(addr)
    db.commit()
    db.refresh(addr)
    return addr


@router.put("/{customer_id}/addresses/{address_id}", response_model=AddressResponse)
def update_address(customer_id: int, address_id: int, data: AddressCreate, db: Session = Depends(get_db)):
    addr = db.query(Address).filter(Address.address_id == address_id, Address.customer_id == customer_id).first()
    if not addr:
        raise HTTPException(status_code=404, detail="地址不存在")
    if data.is_default:
        db.query(Address).filter(Address.customer_id == customer_id).update({"is_default": 0})
    addr.recipient_name = data.recipient_name
    addr.phone = data.phone
    addr.address = data.address
    addr.is_default = data.is_default
    addr.tag = data.tag
    db.commit()
    db.refresh(addr)
    return addr


@router.delete("/{customer_id}/addresses/{address_id}")
def delete_address(customer_id: int, address_id: int, db: Session = Depends(get_db)):
    addr = db.query(Address).filter(Address.address_id == address_id, Address.customer_id == customer_id).first()
    if not addr:
        raise HTTPException(status_code=404, detail="地址不存在")
    db.delete(addr)
    db.commit()
    return {"message": "地址已删除"}


# ========== 收藏管理 ==========
@router.get("/{customer_id}/favorites")
def list_favorites(customer_id: int, db: Session = Depends(get_db)):
    favorites = db.query(Favorite).filter(Favorite.customer_id == customer_id).order_by(Favorite.created_at.desc()).all()
    result = []
    for fav in favorites:
        product = db.query(Product).filter(Product.product_id == fav.product_id).first()
        if product:
            result.append({
                "favorite_id": fav.favorite_id, "product_id": product.product_id,
                "product_name": product.product_name, "unit_price": float(product.unit_price),
                "stock_quantity": product.stock_quantity, "category": product.category,
            })
    return result


@router.post("/{customer_id}/favorites/{product_id}")
def add_favorite(customer_id: int, product_id: int, db: Session = Depends(get_db)):
    exist = db.query(Favorite).filter(Favorite.customer_id == customer_id, Favorite.product_id == product_id).first()
    if exist:
        raise HTTPException(status_code=400, detail="已收藏过该商品")
    fav = Favorite(customer_id=customer_id, product_id=product_id)
    db.add(fav)
    db.commit()
    return {"message": "收藏成功"}


@router.delete("/{customer_id}/favorites/{product_id}")
def remove_favorite(customer_id: int, product_id: int, db: Session = Depends(get_db)):
    fav = db.query(Favorite).filter(Favorite.customer_id == customer_id, Favorite.product_id == product_id).first()
    if not fav:
        raise HTTPException(status_code=404, detail="未收藏该商品")
    db.delete(fav)
    db.commit()
    return {"message": "已取消收藏"}
