import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from app.database import Base

class OrderStatus(str, enum.Enum):
    PENDING = "pending"          # Chờ xác nhận
    PROCESSING = "processing"    # Đang chuẩn bị hàng
    SHIPPING = "shipping"        # Đang giao hàng
    COMPLETED = "completed"      # Giao thành công
    CANCELLED = "cancelled"      # Đã hủy

class PaymentMethod(str, enum.Enum):
    COD = "cod"                  # Thanh toán khi nhận hàng
    BANK_TRANSFER = "bank"       # Chuyển khoản ngân hàng / QR Code
    VNPAY = "vnpay"              # Cổng VNPAY / Momo

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True) # Nullable for guest checkout
    order_code = Column(String(50), unique=True, index=True, nullable=False)
    
    # Customer Info
    customer_name = Column(String(255), nullable=False)
    customer_phone = Column(String(50), nullable=False)
    customer_email = Column(String(255), nullable=True)
    shipping_address = Column(String(500), nullable=False)
    
    # Financials
    total_amount = Column(Float, nullable=False)
    discount_amount = Column(Float, default=0.0)
    final_amount = Column(Float, nullable=False)
    
    # Status & Payment
    payment_method = Column(Enum(PaymentMethod), default=PaymentMethod.COD)
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    note = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    user = relationship("User")

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    
    product_name = Column(String(500), nullable=False)
    product_thumbnail = Column(String(500), nullable=True)
    unit_price = Column(Float, nullable=False)
    quantity = Column(Integer, default=1, nullable=False)
    subtotal = Column(Float, nullable=False)

    # Relationships
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")
