from datetime import datetime, timedelta
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.order import Order
from app.models.product import Product
from app.models.category import Category
from app.models.user import User
from app.models.review import Review
from app.schemas.analytics import (
    RealtimeDashboardData,
    SalesForecastResponse,
    SentimentSummaryResponse,
    CategorySalesStat
)
from app.core.security import require_staff_or_admin
from app.config import settings
from app.services.csv_sync_service import get_sales_dataframe
from app.services.ml_service import train_and_forecast_sales

router = APIRouter(prefix="/analytics", tags=["Analytics & Machine Learning"])

@router.get("/realtime", response_model=RealtimeDashboardData)
def get_realtime_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff_or_admin)
):
    """
    Thống kê tổng quan realtime từ Database và file CSV
    """
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    # Today stats
    today_orders = db.query(Order).filter(Order.created_at >= today_start).all()
    today_revenue = sum(o.final_amount for o in today_orders)
    
    total_products = db.query(Product).count()
    total_customers = db.query(User).filter(User.role == "customer").count()

    # Top selling products
    top_prods = db.query(Product).order_by(Product.sales_count.desc()).limit(5).all()
    top_selling = [
        {
            "id": p.id,
            "name": p.name,
            "brand": p.brand,
            "sales_count": p.sales_count,
            "revenue": p.promo_price * p.sales_count,
            "rating_avg": p.rating_avg,
            "thumbnail": p.thumbnail
        }
        for p in top_prods
    ]

    # Category Breakdown from CSV / DB
    cats = db.query(Category).all()
    cat_stats = []
    total_all_rev = max(1.0, sum(p.promo_price * p.sales_count for p in db.query(Product).all()))
    for c in cats:
        c_rev = sum(p.promo_price * p.sales_count for p in c.products)
        if c_rev > 0:
            cat_stats.append(CategorySalesStat(
                category_name=c.name,
                revenue=c_rev,
                percentage=round((c_rev / total_all_rev) * 100, 1)
            ))

    # Sentiment Breakdown
    reviews = db.query(Review).all()
    total_reviews = len(reviews)
    pos_count = sum(1 for r in reviews if r.sentiment_label == "positive")
    neu_count = sum(1 for r in reviews if r.sentiment_label == "neutral")
    neg_count = sum(1 for r in reviews if r.sentiment_label == "negative")
    pos_ratio = round(pos_count / max(1, total_reviews) * 100, 1)

    recent_revs = [
        {
            "id": r.id,
            "customer_name": r.customer_name,
            "rating": r.rating,
            "comment": r.comment,
            "sentiment_label": r.sentiment_label,
            "sentiment_score": r.sentiment_score,
            "created_at": r.created_at.strftime("%Y-%m-%d %H:%M")
        }
        for r in sorted(reviews, key=lambda x: x.created_at, reverse=True)[:5]
    ]

    sentiment_summary = SentimentSummaryResponse(
        total_reviews=total_reviews,
        positive_count=pos_count,
        neutral_count=neu_count,
        negative_count=neg_count,
        positive_ratio=pos_ratio,
        recent_reviews=recent_revs,
        actionable_insights=[
            "Đa số khách hàng hài lòng với tốc độ đóng gói và hiệu năng laptop ROG / PC Gaming.",
            f"Tỉ lệ tích cực đạt {pos_ratio}%. Cần theo dõi các đánh giá trung tính/tiêu cực về đóng gói vận chuyển ngoại tỉnh."
        ]
    )

    # Hourly trend from CSV
    df = get_sales_dataframe()
    hourly_trend = []
    if not df.empty:
        df_today = df.tail(24)
        for _, row in df_today.iterrows():
            hourly_trend.append({
                "time": str(row['timestamp'])[:16],
                "revenue": float(row['total_revenue']),
                "product_name": str(row['product_name'])
            })

    return RealtimeDashboardData(
        today_revenue=today_revenue,
        today_orders=len(today_orders),
        total_products=total_products,
        total_customers=total_customers,
        hourly_trend=hourly_trend,
        top_selling_products=top_selling,
        category_breakdown=cat_stats,
        sentiment_summary=sentiment_summary
    )

@router.get("/forecast", response_model=SalesForecastResponse)
def get_sales_forecast(
    hours: int = 12,
    current_user: User = Depends(require_staff_or_admin)
):
    """
    Dự báo doanh số chuỗi thời gian (Time-Series) theo giờ bằng Machine Learning
    """
    return train_and_forecast_sales(forecast_hours=hours)

@router.get("/sentiment", response_model=SentimentSummaryResponse)
def get_sentiment_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff_or_admin)
):
    reviews = db.query(Review).all()
    total_reviews = len(reviews)
    pos_count = sum(1 for r in reviews if r.sentiment_label == "positive")
    neu_count = sum(1 for r in reviews if r.sentiment_label == "neutral")
    neg_count = sum(1 for r in reviews if r.sentiment_label == "negative")
    pos_ratio = round(pos_count / max(1, total_reviews) * 100, 1)

    return SentimentSummaryResponse(
        total_reviews=total_reviews,
        positive_count=pos_count,
        neutral_count=neu_count,
        negative_count=neg_count,
        positive_ratio=pos_ratio,
        recent_reviews=[],
        actionable_insights=[
            "Khách hàng đánh giá rất cao chất lượng phần cứng ASUS và linh kiện PC.",
            "Nên duy trì hỗ trợ kỹ thuật cài đặt phần mềm online cho người dùng mới."
        ]
    )

@router.get("/export-csv")
def export_sales_csv(current_user: User = Depends(require_staff_or_admin)):
    """
    Tải file CSV lịch sử bán hàng realtime theo ngày/giờ
    """
    if not os.path.exists(settings.CSV_SALES_PATH):
        raise HTTPException(status_code=404, detail="File CSV chưa có dữ liệu")
    return FileResponse(
        path=settings.CSV_SALES_PATH,
        filename="gearvn_sales_realtime.csv",
        media_type="text/csv"
    )
