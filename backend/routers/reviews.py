from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models import Review, Order, OrderDetail, Customer

router = APIRouter(prefix="/api/reviews", tags=["评价"])


@router.post("/")
def create_review(data: dict, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.order_id == data.get("order_id")).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    if order.status != "COMPLETED":
        raise HTTPException(status_code=400, detail="仅已完成的订单可以评价")
    rating = data.get("rating", 5)
    if not isinstance(rating, int) or rating < 1 or rating > 5:
        raise HTTPException(status_code=400, detail="评分必须在1-5之间")
    product_id = data.get("product_id")
    exists = db.query(Review).filter(
        Review.order_id == order.order_id, Review.product_id == product_id,
        Review.customer_id == order.customer_id
    ).first()
    if exists:
        raise HTTPException(status_code=400, detail="已评价过该商品")
    review = Review(order_id=order.order_id, product_id=product_id,
                    customer_id=order.customer_id, rating=rating,
                    content=data.get("content", ""))
    db.add(review)
    db.commit()
    return {"message": "评价成功", "review_id": review.review_id}


@router.get("/product/{product_id}")
def product_reviews(product_id: int, page: int = Query(1), page_size: int = Query(10), db: Session = Depends(get_db)):
    total = db.query(Review).filter(Review.product_id == product_id).count()
    reviews = db.query(Review).filter(Review.product_id == product_id).order_by(
        Review.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    result = []
    for r in reviews:
        customer = db.query(Customer).filter(Customer.customer_id == r.customer_id).first()
        result.append({"review_id": r.review_id, "order_id": r.order_id, "product_id": r.product_id,
                       "customer_id": r.customer_id,
                       "customer_name": customer.customer_name if customer else "匿名用户",
                       "rating": r.rating, "content": r.content, "created_at": r.created_at})
    avg_r = db.query(func.avg(Review.rating)).filter(Review.product_id == product_id).scalar()
    return {"items": result, "total": total, "page": page, "page_size": page_size,
            "avg_rating": round(float(avg_r), 1) if avg_r else 0.0}
