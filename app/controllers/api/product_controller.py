from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, asc
from app.database import get_db
from app.models.product import Product
from app.models.category import Category
from app.models.user import User
from app.schemas.product import ProductCreate, ProductUpdate, ProductOut
from app.core.security import require_staff_or_admin

router = APIRouter(prefix="/products", tags=["Products"])

@router.get("/", response_model=List[ProductOut])
def get_products(
    db: Session = Depends(get_db),
    category_id: Optional[int] = None,
    category_slug: Optional[str] = None,
    brand: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    search: Optional[str] = None,
    is_flash_sale: Optional[bool] = None,
    is_featured: Optional[bool] = None,
    pc_part_type: Optional[str] = None,
    cpu: Optional[str] = None,
    gpu: Optional[str] = None,
    ram: Optional[str] = None,
    sort_by: Optional[str] = "newest",
    limit: int = 50,
    offset: int = 0
):
    query = db.query(Product)

    if category_slug:
        cat = db.query(Category).filter(Category.slug == category_slug).first()
        if cat:
            query = query.filter(Product.category_id == cat.id)
    elif category_id:
        query = query.filter(Product.category_id == category_id)

    if brand:
        query = query.filter(Product.brand.ilike(f"%{brand}%"))
    if min_price is not None:
        query = query.filter(Product.promo_price >= min_price)
    if max_price is not None:
        query = query.filter(Product.promo_price <= max_price)
    if is_flash_sale is not None:
        query = query.filter(Product.is_flash_sale == is_flash_sale)
    if is_featured is not None:
        query = query.filter(Product.is_featured == is_featured)
    if pc_part_type:
        query = query.filter(Product.pc_part_type == pc_part_type)

    # GearVN Specs Filter
    if cpu:
        query = query.filter(or_(Product.name.ilike(f"%{cpu}%"), Product.specs_json.ilike(f"%{cpu}%")))
    if gpu:
        query = query.filter(or_(Product.name.ilike(f"%{gpu}%"), Product.specs_json.ilike(f"%{gpu}%")))
    if ram:
        query = query.filter(or_(Product.name.ilike(f"%{ram}%"), Product.specs_json.ilike(f"%{ram}%")))

    # Free text search
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

    # Sorting
    if sort_by == "price_asc":
        query = query.order_by(asc(Product.promo_price))
    elif sort_by == "price_desc":
        query = query.order_by(desc(Product.promo_price))
    elif sort_by == "rating":
        query = query.order_by(desc(Product.rating_avg), desc(Product.rating_count))
    elif sort_by == "bestseller":
        query = query.order_by(desc(Product.sales_count))
    else: # newest
        query = query.order_by(desc(Product.created_at))

    products = query.offset(offset).limit(limit).all()
    return products

@router.get("/by-slug/{slug}", response_model=ProductOut)
def get_product_by_slug(slug: str, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.slug == slug).first()
    if not product:
        raise HTTPException(status_code=404, detail="Không tìm thấy sản phẩm")
    # Increment view count
    product.view_count += 1
    db.commit()
    db.refresh(product)
    return product

@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Không tìm thấy sản phẩm")
    return product

@router.post("/", response_model=ProductOut)
def create_product(
    prod_in: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff_or_admin)
):
    existing = db.query(Product).filter(Product.slug == prod_in.slug).first()
    if existing:
        raise HTTPException(status_code=400, detail="Slug sản phẩm đã tồn tại")

    product = Product(**prod_in.dict())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

@router.put("/{product_id}", response_model=ProductOut)
def update_product(
    product_id: int,
    prod_in: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff_or_admin)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Không tìm thấy sản phẩm")

    for field, val in prod_in.dict(exclude_unset=True).items():
        setattr(product, field, val)

    db.commit()
    db.refresh(product)
    return product

@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff_or_admin)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Không tìm thấy sản phẩm")

    db.delete(product)
    db.commit()
    return {"message": "Đã xóa sản phẩm thành công", "product_id": product_id}
