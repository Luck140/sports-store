from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database import get_db
from models import Notification

router = APIRouter(prefix="/api/notifications", tags=["通知"])


@router.get("/{customer_id}")
def list_notifications(customer_id: int, page: int = 1, page_size: int = 20, db: Session = Depends(get_db)):
    q = db.query(Notification).filter(Notification.customer_id == customer_id).order_by(Notification.created_at.desc())
    total = q.count()
    tp = max(1, (total + page_size - 1) // page_size)
    items = q.offset((page - 1) * page_size).limit(page_size).all()
    return {"items": items, "total": total, "page": page, "page_size": page_size, "total_pages": tp}


@router.post("/{customer_id}/read-all")
def mark_all_read(customer_id: int, db: Session = Depends(get_db)):
    db.query(Notification).filter(Notification.customer_id == customer_id, Notification.is_read == 0).update({"is_read": 1})
    db.commit()
    return {"message": "全部已读"}


@router.get("/{customer_id}/unread-count")
def unread_count(customer_id: int, db: Session = Depends(get_db)):
    return {"count": db.query(Notification).filter(Notification.customer_id == customer_id, Notification.is_read == 0).count()}
