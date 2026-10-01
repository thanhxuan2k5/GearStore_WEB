from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class SalesHourlyStat(BaseModel):
    hour: int
    date: str
    revenue: float
    order_count: int

class CategorySalesStat(BaseModel):
    category_name: str
    revenue: float
    percentage: float

class ForecastPoint(BaseModel):
    time_label: str # e.g. "2026-10-01 14:00" or "Day +1"
    predicted_revenue: float
    lower_bound: float
    upper_bound: float

class SalesForecastResponse(BaseModel):
    model_name: str
    last_trained_at: str
    mae_score: float
    r2_score: float
    historical_revenue: List[Dict[str, Any]]
    forecast: List[ForecastPoint]
    summary_insight: str

class SentimentSummaryResponse(BaseModel):
    total_reviews: int
    positive_count: int
    neutral_count: int
    negative_count: int
    positive_ratio: float
    recent_reviews: List[Dict[str, Any]]
    actionable_insights: List[str]

class RealtimeDashboardData(BaseModel):
    today_revenue: float
    today_orders: int
    total_products: int
    total_customers: int
    hourly_trend: List[Dict[str, Any]]
    top_selling_products: List[Dict[str, Any]]
    category_breakdown: List[CategorySalesStat]
    sentiment_summary: SentimentSummaryResponse
