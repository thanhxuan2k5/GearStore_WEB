import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, Base, get_db
from app.core.seed_data import seed_database
from app.views import templates
from app.controllers import web_router, api_router

# ==============================================================================
# 1. MODEL LAYER INITIALIZATION
# ==============================================================================
# Khởi tạo các bảng cơ sở dữ liệu từ tầng Models
Base.metadata.create_all(bind=engine)

# ==============================================================================
# 2. APPLICATION INITIALIZATION
# ==============================================================================
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Hệ thống E-Commerce Công Nghệ GearVN theo mô hình MVC tích hợp AI Assistant, RAG Nội Bộ và ML Dự Báo Doanh Số Realtime",
    version="2.0.0"
)

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==============================================================================
# 3. VIEW LAYER SETUP
# ==============================================================================
# Cung cấp Static Assets (CSS, JS, Hình ảnh) cho tầng View
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# ==============================================================================
# 4. CONTROLLER LAYER MOUNTING
# ==============================================================================
# 4.1. Gắn các Web Controllers (Storefront, Admin & Staff Portal, Auth views)
app.include_router(web_router)

# 4.2. Gắn các RESTful API Controllers (Data Endpoints)
app.include_router(api_router, prefix=settings.API_V1_STR)

# ==============================================================================
# 5. STARTUP LIFECYCLE & SEED DATA
# ==============================================================================
@app.on_event("startup")
def on_startup():
    """Khởi tạo dữ liệu mẫu hệ thống nếu cơ sở dữ liệu trống"""
    db = next(get_db())
    try:
        seed_database(db)
    finally:
        db.close()
