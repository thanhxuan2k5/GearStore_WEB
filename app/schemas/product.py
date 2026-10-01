from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime

class ProductBase(BaseModel):
    category_id: int
    name: str
    slug: str
    brand: str
    original_price: float
    promo_price: float
    stock_quantity: int = 50
    thumbnail: Optional[str] = None
    images_json: Optional[str] = "[]"
    short_desc: Optional[str] = None
    full_desc: Optional[str] = None
    specs_json: Optional[str] = "{}"
    is_flash_sale: bool = False
    is_featured: bool = False
    is_best_seller: bool = False
    pc_part_type: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    category_id: Optional[int] = None
    name: Optional[str] = None
    slug: Optional[str] = None
    brand: Optional[str] = None
    original_price: Optional[float] = None
    promo_price: Optional[float] = None
    stock_quantity: Optional[int] = None
    thumbnail: Optional[str] = None
    images_json: Optional[str] = None
    short_desc: Optional[str] = None
    full_desc: Optional[str] = None
    specs_json: Optional[str] = None
    is_flash_sale: Optional[bool] = None
    is_featured: Optional[bool] = None
    is_best_seller: Optional[bool] = None
    pc_part_type: Optional[str] = None

class ProductOut(ProductBase):
    id: int
    rating_avg: float
    rating_count: int
    view_count: int
    sales_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ProductFilterParams(BaseModel):
    category_id: Optional[int] = None
    brand: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    search: Optional[str] = None
    cpu: Optional[str] = None
    gpu: Optional[str] = None
    ram: Optional[str] = None
    storage: Optional[str] = None
    is_flash_sale: Optional[bool] = None
    pc_part_type: Optional[str] = None
    sort_by: Optional[str] = "newest" # 'newest', 'price_asc', 'price_desc', 'rating', 'bestseller'
