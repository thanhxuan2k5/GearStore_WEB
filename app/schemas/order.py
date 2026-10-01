from typing import List, Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime
from app.models.order import OrderStatus, PaymentMethod

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = 1

class OrderCreate(BaseModel):
    customer_name: str
    customer_phone: str
    customer_email: Optional[EmailStr] = None
    shipping_address: str
    payment_method: PaymentMethod = PaymentMethod.COD
    note: Optional[str] = None
    discount_amount: float = 0.0
    items: List[OrderItemCreate]

class OrderItemOut(BaseModel):
    id: int
    product_id: int
    product_name: str
    product_thumbnail: Optional[str]
    unit_price: float
    quantity: int
    subtotal: float

    class Config:
        from_attributes = True

class OrderOut(BaseModel):
    id: int
    order_code: str
    user_id: Optional[int]
    customer_name: str
    customer_phone: str
    customer_email: Optional[str]
    shipping_address: str
    total_amount: float
    discount_amount: float
    final_amount: float
    payment_method: PaymentMethod
    status: OrderStatus
    note: Optional[str]
    created_at: datetime
    items: List[OrderItemOut] = []

    class Config:
        from_attributes = True

class OrderStatusUpdate(BaseModel):
    status: OrderStatus
