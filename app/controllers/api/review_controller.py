from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.review import Review
from app.models.product import Product
from app.models.user import User
from app.schemas.review import ReviewCreate, ReviewOut
from app.core.security import get_current_user_optional, require_staff_or_admin
from app.services.ml_service import classify_review_sentiment

router = APIRouter(prefix="/reviews", tags=["Reviews & Sentiment"])

@router.get("/product/{product_id}", response_model=List[ReviewOut])
def get_product_reviews(product_id: int, db: Session = Depends(get_db)):
    reviews = db.query(Review).filter(
        Review.product_id == product_id,
        Review.is_approved == 1
    ).order_by(Review.created_at.desc()).all()
    return reviews

@router.post("/", response_model=ReviewOut)
def submit_review(
    review_in: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    product = db.query(Product).filter(Product.id == review_in.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Sản phẩm không tồn tại")

    # 1. Run ML Sentiment Analysis Model
    label, confidence = classify_review_sentiment(review_in.comment)

    # 2. Create Review Record
    review = Review(
        product_id=review_in.product_id,
        user_id=current_user.id if current_user else None,
        customer_name=review_in.customer_name,
        customer_phone=review_in.customer_phone,
        rating=max(1, min(5, review_in.rating)),
        comment=review_in.comment,
        sentiment_label=label,
        sentiment_score=confidence,
        is_approved=1
    )
    db.add(review)
    db.flush()

    # 3. Recalculate Product average rating
    stats = db.query(
        func.avg(Review.rating).label("avg_rating"),
        func.count(Review.id).label("count_rating")
    ).filter(Review.product_id == product.id).first()

    if stats and stats.count_rating > 0:
        product.rating_avg = round(float(stats.avg_rating), 1)
        product.rating_count = stats.count_rating

    db.commit()
    db.refresh(review)
    return review

@router.get("/admin/all", response_model=List[ReviewOut])
def get_all_reviews_admin(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff_or_admin),
    limit: int = 100
):
    reviews = db.query(Review).order_by(Review.created_at.desc()).limit(limit).all()
    return reviews
