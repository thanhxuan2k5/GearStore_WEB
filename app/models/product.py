from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    name = Column(String(500), index=True, nullable=False)
    slug = Column(String(500), unique=True, index=True, nullable=False)
    brand = Column(String(100), index=True, nullable=False)
    
    # Pricing
    original_price = Column(Float, nullable=False)
    promo_price = Column(Float, nullable=False)
    stock_quantity = Column(Integer, default=50)
    
    # Content & Media
    thumbnail = Column(String(500), nullable=True)
    images_json = Column(Text, default="[]") # JSON list of extra image URLs
    short_desc = Column(Text, nullable=True)
    full_desc = Column(Text, nullable=True)
    
    # GearVN Tech Specs stored in structured JSON
    # e.g. {"cpu": "Intel Core i7-14700HX", "gpu": "RTX 4070 8GB", "ram": "16GB DDR5", "storage": "1TB NVMe SSD", "screen": "16 inch 2.5K 165Hz", "socket": "LGA1700", "wattage": 750}
    specs_json = Column(Text, default="{}")
    
    # Storefront flags
    is_flash_sale = Column(Boolean, default=False)
    is_featured = Column(Boolean, default=False)
    is_best_seller = Column(Boolean, default=False)
    
    # PC Builder Part Type (e.g., 'cpu', 'mainboard', 'ram', 'vga', 'storage', 'psu', 'case', 'cooler', 'monitor')
    pc_part_type = Column(String(50), nullable=True, index=True)
    
    # Ratings & Metrics
    rating_avg = Column(Float, default=5.0)
    rating_count = Column(Integer, default=0)
    view_count = Column(Integer, default=0)
    sales_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    category = relationship("Category", back_populates="products")
    reviews = relationship("Review", back_populates="product", cascade="all, delete-orphan")
    order_items = relationship("OrderItem", back_populates="product")
