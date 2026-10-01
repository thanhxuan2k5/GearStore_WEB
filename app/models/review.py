from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    customer_name = Column(String(255), nullable=False)
    customer_phone = Column(String(50), nullable=True)
    rating = Column(Integer, nullable=False, default=5) # 1 to 5 stars
    comment = Column(Text, nullable=False)
    
    # ML Sentiment Analysis fields
    # Positive (Tích cực), Neutral (Trung tính), Negative (Tiêu cực)
    sentiment_label = Column(String(50), default="positive") 
    sentiment_score = Column(Float, default=1.0) # Confidence score 0.0 to 1.0
    
    is_approved = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    product = relationship("Product", back_populates="reviews")
    user = relationship("User")
