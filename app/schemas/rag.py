from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class InternalDocBase(BaseModel):
    title: str
    category: str = "Chính sách bảo hành"
    content_text: str
    tags: Optional[str] = None

class InternalDocCreate(InternalDocBase):
    pass

class InternalDocUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    content_text: Optional[str] = None
    tags: Optional[str] = None

class InternalDocOut(InternalDocBase):
    id: int
    filename: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class RAGQueryRequest(BaseModel):
    query: str
    top_k: int = 3
    space_category: Optional[str] = None # Lọc theo Không gian / Danh mục tài liệu

class RAGCitation(BaseModel):
    doc_id: int
    title: str
    category: str
    snippet: str
    score: float

class RAGQueryResponse(BaseModel):
    answer: str
    citations: List[RAGCitation] = []
    vector_space_used: str = "Tất cả không gian"
    dense_model_active: bool = False
