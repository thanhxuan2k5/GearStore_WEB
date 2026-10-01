from fastapi import APIRouter
from app.controllers.api.auth_controller import router as auth_router
from app.controllers.api.category_controller import router as categories_router
from app.controllers.api.product_controller import router as products_router
from app.controllers.api.order_controller import router as orders_router
from app.controllers.api.review_controller import router as reviews_router
from app.controllers.api.ai_controller import router as ai_router
from app.controllers.api.rag_controller import router as rag_router
from app.controllers.api.analytics_controller import router as analytics_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(categories_router)
api_router.include_router(products_router)
api_router.include_router(orders_router)
api_router.include_router(reviews_router)
api_router.include_router(ai_router)
api_router.include_router(rag_router)
api_router.include_router(analytics_router)
