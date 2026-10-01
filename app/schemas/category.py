from typing import Optional, List
from pydantic import BaseModel

class CategoryBase(BaseModel):
    name: str
    slug: str
    parent_id: Optional[int] = None
    icon: Optional[str] = None
    image_url: Optional[str] = None
    description: Optional[str] = None
    order_index: int = 0

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    parent_id: Optional[int] = None
    icon: Optional[str] = None
    image_url: Optional[str] = None
    description: Optional[str] = None
    order_index: Optional[int] = None

class CategoryOut(CategoryBase):
    id: int
    children: List["CategoryOut"] = []

    class Config:
        from_attributes = True

CategoryOut.update_forward_refs()
