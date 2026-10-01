from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class AIChatMessage(BaseModel):
    role: str # 'user' or 'assistant' or 'system'
    content: str

class AIChatRequest(BaseModel):
    message: str
    conversation_history: Optional[List[AIChatMessage]] = []
    budget: Optional[float] = None
    category_slug: Optional[str] = None

class RecommendedProductItem(BaseModel):
    id: int
    name: str
    slug: str
    brand: str
    promo_price: float
    original_price: float
    thumbnail: Optional[str] = None
    specs: Dict[str, Any] = {}
    reason: str

class AIChatResponse(BaseModel):
    reply: str
    intent: Optional[str] = "consultation" # 'consultation', 'pc_builder', 'price_check', 'faq'
    recommended_products: List[RecommendedProductItem] = []
    suggested_questions: List[str] = []

class PCBuilderCompatibilityRequest(BaseModel):
    cpu_id: Optional[int] = None
    mainboard_id: Optional[int] = None
    ram_id: Optional[int] = None
    vga_id: Optional[int] = None
    psu_id: Optional[int] = None
    case_id: Optional[int] = None
    cooler_id: Optional[int] = None
    storage_id: Optional[int] = None

class PCBuilderCompatibilityResponse(BaseModel):
    is_compatible: bool
    issues: List[str] = []
    warnings: List[str] = []
    estimated_wattage: int = 0
    recommended_psu_wattage: int = 500
    total_price: float = 0.0
