# Backward-compatible bridge to app.controllers.api
from app.controllers.api import (
    api_router,
    auth_router,
    categories_router,
    products_router,
    orders_router,
    reviews_router,
    ai_router,
    rag_router,
    analytics_router,
)

__all__ = [
    "api_router",
    "auth_router",
    "categories_router",
    "products_router",
    "orders_router",
    "reviews_router",
    "ai_router",
    "rag_router",
    "analytics_router",
]
