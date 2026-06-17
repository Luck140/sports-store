from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Banner
from schemas import BannerResponse

router = APIRouter(prefix="/api/banners", tags=["横幅"])


@router.get("/", response_model=list[BannerResponse])
def get_active_banners(db: Session = Depends(get_db)):
    return db.query(Banner).filter(Banner.is_active == 1).order_by(Banner.sort_order).all()
