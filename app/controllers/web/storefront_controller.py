import json
from typing import Optional
from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, asc

from app.database import get_db
from app.views import templates
from app.models.product import Product
from app.models.category import Category
from app.models.order import Order
from app.models.review import Review

router = APIRouter(tags=["Storefront Web Controller"])

@router.get("/")
def home_page(request: Request, db: Session = Depends(get_db)):
    """Trang chủ GearVN: Flash sale và Laptop nổi bật"""
    flash_sales = db.query(Product).filter(Product.is_flash_sale == True).limit(4).all()
    featured_laptops = db.query(Product).filter(
        or_(Product.is_featured == True, Product.name.ilike("%Laptop%"))
    ).limit(8).all()

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "flash_sale_products": flash_sales,
            "featured_laptops": featured_laptops
        }
    )

@router.get("/products")
def product_list_page(
    request: Request,
    db: Session = Depends(get_db),
    category_slug: Optional[str] = None,
    category_id: Optional[int] = None,
    brand: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    search: Optional[str] = None,
    cpu: Optional[str] = None,
    gpu: Optional[str] = None,
    ram: Optional[str] = None,
    is_flash_sale: Optional[bool] = None,
    sort_by: Optional[str] = "newest"
):
    """Trang danh sách sản phẩm với bộ lọc thông số chi tiết"""
    query = db.query(Product)
    category_name = None

    if category_slug:
        cat = db.query(Category).filter(Category.slug == category_slug).first()
        if cat:
            query = query.filter(Product.category_id == cat.id)
            category_name = cat.name
    elif category_id:
        cat = db.query(Category).filter(Category.id == category_id).first()
        if cat:
            query = query.filter(Product.category_id == cat.id)
            category_name = cat.name

    if brand:
        query = query.filter(Product.brand.ilike(f"%{brand}%"))
    if min_price is not None:
        query = query.filter(Product.promo_price >= min_price)
    if max_price is not None:
        query = query.filter(Product.promo_price <= max_price)
    if is_flash_sale:
        query = query.filter(Product.is_flash_sale == True)
    if cpu:
        query = query.filter(or_(Product.name.ilike(f"%{cpu}%"), Product.specs_json.ilike(f"%{cpu}%")))
    if gpu:
        query = query.filter(or_(Product.name.ilike(f"%{gpu}%"), Product.specs_json.ilike(f"%{gpu}%")))
    if ram:
        query = query.filter(or_(Product.name.ilike(f"%{ram}%"), Product.specs_json.ilike(f"%{ram}%")))

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Product.name.ilike(search_term),
                Product.brand.ilike(search_term),
                Product.short_desc.ilike(search_term),
                Product.specs_json.ilike(search_term)
            )
        )
        category_name = f"Kết quả tìm kiếm cho '{search}'"

    if sort_by == "price_asc":
        query = query.order_by(asc(Product.promo_price))
    elif sort_by == "price_desc":
        query = query.order_by(desc(Product.promo_price))
    elif sort_by == "rating":
        query = query.order_by(desc(Product.rating_avg))
    elif sort_by == "bestseller":
        query = query.order_by(desc(Product.sales_count))
    else:
        query = query.order_by(desc(Product.created_at))

    products = query.all()
    categories = db.query(Category).all()

    return templates.TemplateResponse(
        "product_list.html",
        {
            "request": request,
            "products": products,
            "categories": categories,
            "category_name": category_name,
            "category_slug": category_slug,
            "brand": brand,
            "min_price": min_price,
            "max_price": max_price,
            "cpu": cpu,
            "gpu": gpu,
            "ram": ram,
            "search_query": search,
            "sort_by": sort_by
        }
    )

@router.get("/product/{slug}")
def product_detail_page(slug: str, request: Request, db: Session = Depends(get_db)):
    """Trang chi tiết sản phẩm và đánh giá"""
    product = db.query(Product).filter(Product.slug == slug).first()
    if not product:
        try:
            product = db.query(Product).filter(Product.id == int(slug)).first()
        except ValueError:
            product = None
    
    if not product:
        return templates.TemplateResponse("product_list.html", {"request": request, "products": []})

    # Tăng lượt xem
    product.view_count += 1
    db.commit()

    specs = {}
    try:
        specs = json.loads(product.specs_json) if product.specs_json else {}
    except Exception:
        pass

    reviews = db.query(Review).filter(
        Review.product_id == product.id,
        Review.is_approved == 1
    ).order_by(desc(Review.created_at)).all()

    return templates.TemplateResponse(
        "product_detail.html",
        {
            "request": request,
            "product": product,
            "specs": specs,
            "reviews": reviews
        }
    )

@router.get("/pc-builder")
def pc_builder_page(request: Request):
    """Trang xây dựng cấu hình PC tương thích"""
    return templates.TemplateResponse("pc_builder.html", {"request": request})

@router.get("/cart")
def cart_page(request: Request):
    """Trang giỏ hàng mua sắm"""
    return templates.TemplateResponse("cart.html", {"request": request})

@router.get("/order-success")
def order_success_page(order_code: str, request: Request, db: Session = Depends(get_db)):
    """Trang thông báo đặt hàng thành công"""
    order = db.query(Order).filter(Order.order_code == order_code).first()
    return templates.TemplateResponse("order_success.html", {"request": request, "order": order})

@router.get("/profile")
def profile_page(request: Request):
    """Trang thông tin tài khoản cá nhân"""
    return templates.TemplateResponse("profile.html", {"request": request})
