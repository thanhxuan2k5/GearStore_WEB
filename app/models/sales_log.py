from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime
from app.database import Base

class SalesLog(Base):
    __tablename__ = "sales_logs"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, index=True, nullable=True)
    product_id = Column(Integer, index=True, nullable=True)
    product_name = Column(String(500), nullable=True)
    category_id = Column(Integer, index=True, nullable=True)
    category_name = Column(String(255), nullable=True)
    quantity = Column(Integer, default=1)
    unit_price = Column(Float, default=0.0)
    total_revenue = Column(Float, default=0.0)
    
    # Time breakdown for hourly/daily ML models
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    date_str = Column(String(20), index=True) # YYYY-MM-DD
    hour_int = Column(Integer, index=True)    # 0 to 23
    day_of_week = Column(Integer)             # 0=Monday, 6=Sunday
    month_int = Column(Integer)               # 1 to 12
