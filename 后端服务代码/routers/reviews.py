from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from models import Review, Customer, Order, OrderDetail
from schemas import ReviewCreate, ReviewResponse

router = APIRouter(prefix="/api/reviews", tags=["评价"])


@router.post("/")
def create_review(data: ReviewCreate, db: Session = Depends(get_db)):
    if data.rating < 1 or data.rating > 5: raise HTTPException(400, detail="评分范围1-5")
    o = db.query(Order).filter(Order.order_id == data.order_id).first()
    if not o: raise HTTPException(404, detail="订单不存在")
    d = db.query(OrderDetail).filter(OrderDetail.order_id == data.order_id, OrderDetail.product_id == data.product_id).first()
    if not d: raise HTTPException(400, detail="该订单不包含此商品")
    r = Review(order_id=data.order_id, product_id=data.product_id,
               customer_id=data.customer_id or o.customer_id, rating=data.rating, content=data.content)
    db.add(r); db.commit(); db.refresh(r)
    return r


@router.get("/product/{product_id}")
def list_reviews(product_id: int, page: int = 1, page_size: int = 10, db: Session = Depends(get_db)):
    q = db.query(Review).filter(Review.product_id == product_id).order_by(Review.created_at.desc())
    total = q.count()
    tp = max(1, (total + page_size - 1) // page_size)
    items = [ReviewResponse(review_id=r.review_id, order_id=r.order_id, product_id=r.product_id,
                            customer_id=r.customer_id,
                            customer_name=(db.query(Customer).filter(Customer.customer_id == r.customer_id).first().customer_name or "") if db.query(Customer).filter(Customer.customer_id == r.customer_id).first() else "",
                            rating=r.rating, content=r.content, created_at=r.created_at)
             for r in q.offset((page - 1) * page_size).limit(page_size).all()]
    return {"items": items, "total": total, "page": page, "page_size": page_size, "total_pages": tp}
