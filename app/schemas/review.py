from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class ReviewCreate(BaseModel):
    product_id: int
    customer_name: str
    customer_phone: Optional[str] = None
    rating: int = 5
    comment: str

class ReviewOut(BaseModel):
    id: int
    product_id: int
    customer_name: str
    rating: int
    comment: str
    sentiment_label: Optional[str] = "positive"
    sentiment_score: Optional[float] = 1.0
    created_at: datetime

    class Config:
        from_attributes = True
