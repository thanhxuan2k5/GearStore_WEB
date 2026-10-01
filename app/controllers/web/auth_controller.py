from fastapi import APIRouter, Request
from app.views import templates

router = APIRouter(tags=["Auth Web Controller"])

@router.get("/login")
def login_page(request: Request):
    """Trang đăng nhập độc lập dành cho Khách hàng, Nhân viên và Quản lý"""
    return templates.TemplateResponse("auth/login.html", {"request": request})

@router.get("/register")
def register_page(request: Request):
    """Trang đăng ký tài khoản khách hàng"""
    return templates.TemplateResponse("auth/login.html", {"request": request})

@router.get("/logout")
def logout_page(request: Request):
    """Trang xử lý đăng xuất an toàn"""
    return templates.TemplateResponse("auth/logout.html", {"request": request})
