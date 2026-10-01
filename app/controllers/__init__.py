from fastapi import APIRouter
from app.controllers.web import web_router
from app.controllers.api import api_router

__all__ = ["web_router", "api_router"]
