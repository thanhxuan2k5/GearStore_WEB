import random
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.order import Order, OrderItem, OrderStatus, PaymentMethod
from app.models.product import Product
from app.models.user import User
from app.models.sales_log import SalesLog
from app.schemas.order import OrderCreate, OrderOut, OrderStatusUpdate
from app.core.security import get_current_user_optional, require_staff_or_admin
from app.services.csv_sync_service import append_sales_record

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.post("/", response_model=OrderOut)
def create_order(
    order_in: OrderCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    if not order_in.items:
        raise HTTPException(status_code=400, detail="Giỏ hàng không có sản phẩm")

    total_amount = 0.0
    items_to_create = []

    # Generate Order Code (e.g. GVN-202610-12345)
    now = datetime.utcnow()
    order_code = f"GVN-{now.strftime('%y%m%d%H%M')}-{random.randint(100, 999)}"

    # Validate stock and calculate amount
    for item_req in order_in.items:
        product = db.query(Product).filter(Product.id == item_req.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Sản phẩm ID {item_req.product_id} không tồn tại")
        
        if product.stock_quantity < item_req.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Sản phẩm '{product.name}' chỉ còn {product.stock_quantity} trong kho"
            )

        unit_price = product.promo_price
        subtotal = unit_price * item_req.quantity
        total_amount += subtotal

        # Decrement stock and increment sales count
        product.stock_quantity -= item_req.quantity
        product.sales_count += item_req.quantity

        items_to_create.append({
            "product": product,
            "quantity": item_req.quantity,
            "unit_price": unit_price,
            "subtotal": subtotal
        })

    final_amount = max(0.0, total_amount - order_in.discount_amount)

    order = Order(
        user_id=current_user.id if current_user else None,
        order_code=order_code,
        customer_name=order_in.customer_name,
        customer_phone=order_in.customer_phone,
        customer_email=order_in.customer_email,
        shipping_address=order_in.shipping_address,
        total_amount=total_amount,
        discount_amount=order_in.discount_amount,
        final_amount=final_amount,
        payment_method=order_in.payment_method,
        status=OrderStatus.PENDING,
        note=order_in.note
    )
    db.add(order)
    db.flush() # get order.id

    # Create order items & log realtime sales
    for it in items_to_create:
        p = it["product"]
        order_item = OrderItem(
            order_id=order.id,
            product_id=p.id,
            product_name=p.name,
            product_thumbnail=p.thumbnail,
            unit_price=it["unit_price"],
            quantity=it["quantity"],
            subtotal=it["subtotal"]
        )
        db.add(order_item)

        # 1. Append to Realtime CSV
        cat_name = p.category.name if p.category else "Linh kiện & Thiết bị"
        append_sales_record(
            order_code=order.order_code,
            product_id=p.id,
            product_name=p.name,
            category_id=p.category_id,
            category_name=cat_name,
            quantity=it["quantity"],
            unit_price=it["unit_price"],
            total_revenue=it["subtotal"],
            customer_name=order_in.customer_name,
            custom_dt=now
        )

        # 2. Add to SalesLog table
        sales_log = SalesLog(
            order_id=order.id,
            product_id=p.id,
            product_name=p.name,
            category_id=p.category_id,
            category_name=cat_name,
            quantity=it["quantity"],
            unit_price=it["unit_price"],
            total_revenue=it["subtotal"],
            timestamp=now,
            date_str=now.strftime("%Y-%m-%d"),
            hour_int=now.hour,
            day_of_week=now.weekday(),
            month_int=now.month
        )
        db.add(sales_log)

    db.commit()
    db.refresh(order)
    return order

@router.get("/", response_model=List[OrderOut])
def get_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff_or_admin),
    limit: int = 50,
    offset: int = 0
):
    orders = db.query(Order).order_by(Order.created_at.desc()).offset(offset).limit(limit).all()
    return orders

@router.get("/{order_code}", response_model=OrderOut)
def get_order_by_code(order_code: str, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.order_code == order_code).first()
    if not order:
        raise HTTPException(status_code=404, detail="Không tìm thấy đơn hàng")
    return order

@router.put("/{order_id}/status", response_model=OrderOut)
def update_order_status(
    order_id: int,
    status_update: OrderStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff_or_admin)
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Không tìm thấy đơn hàng")
    
    order.status = status_update.status
    db.commit()
    db.refresh(order)
    return order
