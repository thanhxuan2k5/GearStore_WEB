from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.ai import (
    AIChatRequest,
    AIChatResponse,
    PCBuilderCompatibilityRequest,
    PCBuilderCompatibilityResponse
)
from app.services.ai_service import ai_sales_assistant
from app.services.pc_builder_service import pc_builder_service

router = APIRouter(prefix="/ai", tags=["AI Sales Assistant"])

@router.post("/chat", response_model=AIChatResponse)
def ai_chat_consultation(request: AIChatRequest, db: Session = Depends(get_db)):
    """
    Endpoint tư vấn bán hàng thông minh qua AI cho khách hàng
    Tự động phân tích nhu cầu, ngân sách và gợi ý các sản phẩm phù hợp nhất
    """
    return ai_sales_assistant.process_consultation(db, request)

@router.post("/pc-builder-check", response_model=PCBuilderCompatibilityResponse)
def check_pc_compatibility(req: PCBuilderCompatibilityRequest, db: Session = Depends(get_db)):
    """
    Kiểm tra tính tương thích giữa các linh kiện trong dàn PC đã chọn
    (Socket CPU & Mainboard, Chuẩn RAM DDR4/DDR5, Công suất Nguồn PSU...)
    """
    return pc_builder_service.check_compatibility(db, req)
