from fastapi import APIRouter
from app.controllers.web.storefront_controller import router as storefront_router
from app.controllers.web.admin_controller import router as admin_router
from app.controllers.web.auth_controller import router as auth_web_router

web_router = APIRouter()
web_router.include_router(storefront_router)
web_router.include_router(admin_router)
web_router.include_router(auth_web_router)
