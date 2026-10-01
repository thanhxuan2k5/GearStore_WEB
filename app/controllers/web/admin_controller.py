from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db
from app.views import templates
from app.models.product import Product
from app.models.category import Category
from app.models.order import Order
from app.models.internal_doc import InternalDoc
from app.models.user import User

router = APIRouter(prefix="/admin", tags=["Admin & Staff Web Controller"])

@router.get("/dashboard")
def admin_dashboard(request: Request):
    """Bảng điều khiển trung tâm (Dashboard) dành cho Quản lý & Nhân viên"""
    return templates.TemplateResponse("admin/dashboard.html", {"request": request, "active_page": "dashboard"})

@router.get("/products")
def admin_products_page(request: Request, db: Session = Depends(get_db)):
    """Trang quản trị danh mục sản phẩm"""
    products = db.query(Product).order_by(desc(Product.id)).all()
    categories = db.query(Category).all()
    return templates.TemplateResponse(
        "admin/products.html",
        {
            "request": request,
            "products": products,
            "categories": categories,
            "active_page": "products"
        }
    )

@router.get("/categories")
def admin_categories_page(request: Request, db: Session = Depends(get_db)):
    """Trang quản trị chuyên mục sản phẩm"""
    categories = db.query(Category).order_by(Category.order_index.asc()).all()
    return templates.TemplateResponse(
        "admin/categories.html",
        {
            "request": request,
            "categories": categories,
            "active_page": "categories"
        }
    )

@router.get("/orders")
def admin_orders_page(request: Request, db: Session = Depends(get_db)):
    """Trang xử lý và theo dõi đơn hàng"""
    orders = db.query(Order).order_by(desc(Order.created_at)).all()
    return templates.TemplateResponse(
        "admin/orders.html",
        {
            "request": request,
            "orders": orders,
            "active_page": "orders"
        }
    )

@router.get("/rag")
def admin_rag_page(request: Request, db: Session = Depends(get_db)):
    """Trang quản trị Không gian tri thức nội bộ"""
    docs = db.query(InternalDoc).order_by(desc(InternalDoc.created_at)).all()
    raw_spaces = db.query(InternalDoc.category).distinct().all()
    spaces = [s[0] for s in raw_spaces if s[0]]
    default_spaces = ["Chính sách bảo hành", "Tiêu chuẩn kỹ thuật", "Chính sách nội bộ", "Quy trình vận hành"]
    for ds in default_spaces:
        if ds not in spaces:
            spaces.append(ds)

    return templates.TemplateResponse(
        "admin/rag_internal.html",
        {
            "request": request,
            "docs": docs,
            "spaces": spaces,
            "active_page": "rag"
        }
    )

@router.get("/users")
def admin_users_page(request: Request, db: Session = Depends(get_db)):
    """Trang quản lý nhân viên và tài khoản người dùng (chỉ dành cho Quản lý)"""
    users = db.query(User).order_by(desc(User.id)).all()
    return templates.TemplateResponse(
        "admin/users.html",
        {
            "request": request,
            "users": users,
            "active_page": "users"
        }
    )
