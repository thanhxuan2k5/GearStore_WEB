from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from app.database import Base

class InternalDoc(Base):
    __tablename__ = "internal_docs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    category = Column(String(100), default="Quy định bảo hành") # 'Chính sách bảo hành', 'Quy trình đổi trả', 'Chiết khấu nhân viên', 'Hướng dẫn kỹ thuật'
    filename = Column(String(255), nullable=True)
    file_path = Column(String(500), nullable=True)
    content_text = Column(Text, nullable=False)
    tags = Column(String(255), nullable=True) # e.g. "asus, man hinh, doi tra"
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
