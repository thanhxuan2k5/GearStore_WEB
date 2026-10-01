from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, UserRole
from app.schemas.auth import (
    UserRegister, UserLogin, UserOut, Token,
    ChangePasswordRequest, UserCreateAdmin, UserUpdateAdmin
)
from app.core.security import (
    verify_password, get_password_hash, create_access_token,
    get_current_user, require_admin
)

router = APIRouter(prefix="/auth", tags=["Authentication & User Management"])

@router.post("/register", response_model=UserOut)
def register(user_in: UserRegister, db: Session = Depends(get_db)):
    email_clean = user_in.email.strip().lower()
    if email_clean.endswith("@gearvn.com"):
        raise HTTPException(
            status_code=400,
            detail="Tên miền @gearvn.com dành riêng cho tài khoản nội bộ và chỉ do Quản lý (Admin) tạo trên hệ thống."
        )

    existing = db.query(User).filter(User.email == email_clean).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email này đã được đăng ký trên hệ thống")
    
    user = User(
        email=email_clean,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        phone=user_in.phone,
        address=user_in.address,
        role=UserRole.CUSTOMER
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/login-json", response_model=Token)
def login_json(credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email hoặc mật khẩu không chính xác"
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Tài khoản này đã bị khóa")

    access_token = create_access_token(data={"sub": user.email, "role": user.role.value})
    return Token(
        access_token=access_token,
        token_type="bearer",
        user_id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role.value
    )

@router.post("/token", response_model=Token)
def login_form(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email hoặc mật khẩu không chính xác"
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Tài khoản này đã bị khóa")

    access_token = create_access_token(data={"sub": user.email, "role": user.role.value})
    return Token(
        access_token=access_token,
        token_type="bearer",
        user_id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role.value
    )

@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/change-password")
def change_password(
    req: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not verify_password(req.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Mật khẩu hiện tại không chính xác")
    
    if len(req.new_password) < 6:
        raise HTTPException(status_code=400, detail="Mật khẩu mới phải có tối thiểu 6 ký tự")

    current_user.hashed_password = get_password_hash(req.new_password)
    db.commit()
    return {"message": "Đổi mật khẩu thành công!"}


# ==========================================
# ADMIN USER MANAGEMENT APIS
# ==========================================

@router.get("/users", response_model=List[UserOut])
def get_all_users(
    role: Optional[str] = None,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    query = db.query(User)
    if role:
        query = query.filter(User.role == role)
    return query.order_by(User.id.desc()).all()

@router.post("/users", response_model=UserOut)
def create_user_by_admin(
    user_in: UserCreateAdmin,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    email_clean = user_in.email.strip().lower()

    # Nhân viên và Quản lý bắt buộc phải có đuôi @gearvn.com
    if user_in.role in [UserRole.STAFF, UserRole.ADMIN] or str(user_in.role).lower() in ["staff", "admin"]:
        if not email_clean.endswith("@gearvn.com"):
            raise HTTPException(
                status_code=400,
                detail="Tài khoản nhân viên hoặc quản lý bắt buộc phải có tên miền @gearvn.com (Ví dụ: tennhanvien@gearvn.com)"
            )

    existing = db.query(User).filter(User.email == email_clean).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email này đã tồn tại trên hệ thống")

    user = User(
        email=email_clean,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        phone=user_in.phone,
        address=user_in.address,
        role=user_in.role,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.put("/users/{user_id}", response_model=UserOut)
def update_user_by_admin(
    user_id: int,
    user_in: UserUpdateAdmin,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")

    effective_role = user_in.role if user_in.role is not None else user.role

    if user_in.email is not None:
        email_clean = user_in.email.strip().lower()
        if effective_role in [UserRole.STAFF, UserRole.ADMIN] or str(effective_role).lower() in ["staff", "admin"]:
            if not email_clean.endswith("@gearvn.com"):
                raise HTTPException(
                    status_code=400,
                    detail="Tài khoản nhân viên hoặc quản lý bắt buộc phải có tên miền @gearvn.com"
                )
        existing = db.query(User).filter(User.email == email_clean, User.id != user_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email này đã được sử dụng bởi tài khoản khác")
        user.email = email_clean
    elif user_in.role is not None and (user_in.role in [UserRole.STAFF, UserRole.ADMIN] or str(user_in.role).lower() in ["staff", "admin"]):
        if not user.email.lower().endswith("@gearvn.com"):
            raise HTTPException(
                status_code=400,
                detail="Không thể chuyển quyền sang nhân viên/quản lý vì email không có tên miền @gearvn.com"
            )

    if user_in.password:
        if len(user_in.password) < 6:
            raise HTTPException(status_code=400, detail="Mật khẩu phải có tối thiểu 6 ký tự")
        user.hashed_password = get_password_hash(user_in.password)

    if user_in.full_name is not None:
        user.full_name = user_in.full_name
    if user_in.phone is not None:
        user.phone = user_in.phone
    if user_in.address is not None:
        user.address = user_in.address
    if user_in.role is not None:
        user.role = user_in.role
    if user_in.is_active is not None:
        user.is_active = user_in.is_active

    db.commit()
    db.refresh(user)
    return user

@router.delete("/users/{user_id}")
def delete_user_by_admin(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    if user_id == admin.id:
        raise HTTPException(status_code=400, detail="Không thể xóa tài khoản của chính mình")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")

    db.delete(user)
    db.commit()
    return {"message": "Đã xóa tài khoản thành công", "user_id": user_id}
