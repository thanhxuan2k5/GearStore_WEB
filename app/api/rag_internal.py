import os
import shutil
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.internal_doc import InternalDoc
from app.models.user import User
from app.schemas.rag import (
    InternalDocCreate, InternalDocUpdate, InternalDocOut,
    RAGQueryRequest, RAGQueryResponse
)
from app.core.security import require_staff_or_admin
from app.services.rag_service import rag_service
from app.services.doc_extractor import extract_text_from_file

router = APIRouter(prefix="/rag", tags=["Internal RAG Knowledge Base"])

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

SAMPLE_DOCS = [
    {
        "title": "Chính Sách Bảo Hành & Đổi Trả Sản Phẩm Công Nghệ GearVN 2026",
        "category": "Chính sách bảo hành",
        "tags": "bao hanh, doi tra, 1 doi 1, loi nha san xuat",
        "content_text": """1. QUY ĐỊNH ĐỔI TRẢ 1 ĐỔI 1 TRONG 30 NGÀY ĐẦU:
- Áp dụng cho tất cả các sản phẩm Laptop, PC Gaming, Linh kiện phần cứng (CPU, VGA, Mainboard, RAM, SSD, Nguồn) phát sinh lỗi kỹ thuật phần cứng do nhà sản xuất.
- Điều kiện: Sản phẩm còn nguyên vẹn, không móp méo, trầy xước nặng, không có dấu hiệu vào nước hay can thiệp sửa chữa ngoài, đầy đủ hộp (box), sách hướng dẫn và phụ kiện đi kèm.

2. QUY TRÌNH TIẾP NHẬN BẢO HÀNH:
- Bước 1: Nhân viên kỹ thuật kiểm tra ngoại quan và xác nhận số Serial Number (S/N) trên hệ thống ERP GearVN.
- Bước 2: Thời gian kiểm tra lỗi nhanh tại quầy từ 15 - 30 phút.
- Bước 3: Nếu xác định lỗi phần cứng rõ ràng trong 30 ngày đầu, xuất kho đổi ngay sản phẩm mới 100% cùng model cho khách. Trường hợp hết hàng cùng model, khách hàng được đổi sang model tương đương hoặc hoàn tiền 100%."""
    },
    {
        "title": "Quy Định Bảo Hành Màn Hình và Tiêu Chuẩn Điểm Chết (Dead Pixel)",
        "category": "Tiêu chuẩn kỹ thuật",
        "tags": "man hinh, diem chet, dead pixel, asus, lg, samsung",
        "content_text": """TIÊU CHUẨN XỬ LÝ ĐIỂM CHẾT MÀN HÌNH CỦA CÁC HÃNG:
- Hãng ASUS: Đổi mới màn hình nếu có từ 3 điểm chết sáng (Bright dot) hoặc 5 điểm chết tối (Dark dot) trở lên trong vòng 3 năm. Riêng dòng ROG/TUF cao cấp hỗ trợ Zero Bright Dot trong 1 năm đầu.
- Hãng LG: Áp dụng đổi mới/thay panel nếu phát hiện từ 3 điểm chết trở lên đối với màn hình UltraGear và UltraFine.
- Hãng Samsung: Áp dụng theo tiêu chuẩn tối thiểu 5 điểm chết đối với các dòng Odyssey Gaming.
- Khách hàng mua kèm gói 'Bảo Hành VIP GearVN' được hỗ trợ 1 đổi 1 ngay lập tức nếu xuất hiện từ 1 điểm chết bất kỳ trong 3 tháng đầu."""
    },
    {
        "title": "Chính Sách Chiết Khấu Mua Hàng & Phúc Lợi Cho Nhân Viên GearVN",
        "category": "Chính sách nội bộ",
        "tags": "chiet khau nhan vien, mua hang noi bo, tra gop 0%",
        "content_text": """CHÍNH SÁCH MUA HÀNG NỘI BỘ DÀNH CHO NHÂN VIÊN CHÍNH THỨC:
1. Mức giảm giá chiết khấu:
- Linh kiện PC (CPU, Mainboard, VGA, RAM, SSD): Giảm trực tiếp 8% trên giá bán niêm yết hoặc tính theo giá vốn nhập kho + 2% chi phí vận hành (tùy mức nào thấp hơn).
- Gaming Gear (Bàn phím, Chuột, Tai nghe): Giảm 12% - 15%.
- Laptop Gaming & PC Lắp sẵn: Giảm 7% tối đa 3.000.000 VNĐ/sản phẩm.

2. Hạn mức mua hàng: Mỗi nhân viên được hưởng hạn mức tối đa 50.000.000 VNĐ/năm cho người thân và bản thân. Cần đăng ký qua cổng Portal HR trước 24h."""
    },
    {
        "title": "Quy Trình Kiểm Kê & Nhập Xuất Kho Linh Kiện Máy Tính",
        "category": "Quy trình vận hành",
        "tags": "kho, nhap kho, xuat kho, serial, linh kien",
        "content_text": """QUY TRÌNH QUẢN LÝ KHO & BẢO QUẢN THIẾT BỊ:
1. Nhập kho linh kiện:
- Toàn bộ linh kiện phần cứng (CPU, Mainboard, VGA, RAM, SSD) phải được quét mã vạch Serial Number (S/N) vào phần mềm trước khi dán tem niêm phong GearVN.
- Khu vực lưu trữ linh kiện điện tử phải duy trì độ ẩm phòng dưới 60% và nhiệt độ ổn định 22-26 độ C để chống tĩnh điện và oxy hóa chân tiếp xúc.

2. Xuất kho giao hàng:
- Kiểm tra trùng khớp S/N giữa hóa đơn bán hàng và vỏ hộp sản phẩm trước khi bàn giao cho bộ phận Logistics."""
    }
]

@router.post("/query", response_model=RAGQueryResponse)
def query_internal_rag(
    req: RAGQueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff_or_admin)
):
    """
    RAG Chatbot nội bộ dành cho Nhân viên & Quản trị viên
    Hỗ trợ lọc theo Không gian tài liệu (Vector Space / Category)
    """
    return rag_service.answer_query(db, query=req.query, top_k=req.top_k, space_category=req.space_category)

@router.get("/spaces")
def get_vector_spaces(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff_or_admin)
):
    """Lấy danh sách các Không gian Vector (Vector Spaces) hiện có và số lượng tài liệu"""
    spaces = db.query(
        InternalDoc.category,
        func.count(InternalDoc.id).label("doc_count")
    ).group_by(InternalDoc.category).all()

    return [{"space_name": s[0], "doc_count": s[1]} for s in spaces]

@router.get("/docs", response_model=List[InternalDocOut])
def get_internal_docs(
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff_or_admin)
):
    query = db.query(InternalDoc)
    if category and category != "all":
        query = query.filter(InternalDoc.category == category)
    return query.order_by(InternalDoc.created_at.desc()).all()

@router.post("/upload-file", response_model=InternalDocOut)
async def upload_document_file(
    file: UploadFile = File(...),
    category: str = Form("Chính sách bảo hành"),
    title: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff_or_admin)
):
    """
    Tải lên tài liệu dạng file Word (.docx, .doc), PDF (.pdf), Markdown (.md), Text (.txt)
    Tự động giải mã, trích xuất nội dung văn bản và nạp vào Vector DB
    """
    filename = file.filename or "uploaded_document"
    ext = os.path.splitext(filename)[1].lower()

    allowed_exts = [".pdf", ".docx", ".doc", ".md", ".markdown", ".txt"]
    if ext not in allowed_exts:
        raise HTTPException(
            status_code=400,
            detail=f"Định dạng file '{ext}' không hợp lệ. Chỉ chấp nhận các định dạng: .pdf, .docx, .md, .txt"
        )

    # Save file to disk
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    safe_name = f"{timestamp}_{filename}"
    saved_path = os.path.join(UPLOAD_DIR, safe_name)

    try:
        with open(saved_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi lưu trữ file: {str(e)}")

    # Extract text
    try:
        content_text = extract_text_from_file(saved_path, filename)
    except Exception as e:
        if os.path.exists(saved_path):
            os.remove(saved_path)
        raise HTTPException(status_code=400, detail=f"Không thể đọc nội dung file: {str(e)}")

    # Determine Doc Title
    doc_title = title.strip() if (title and title.strip()) else os.path.splitext(filename)[0].replace("_", " ").replace("-", " ")

    # Create record
    doc = InternalDoc(
        title=doc_title,
        category=category.strip() if category else "Chính sách chung",
        filename=filename,
        file_path=saved_path,
        content_text=content_text,
        tags=tags
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc

@router.get("/docs/{doc_id}/download")
def download_document_file(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff_or_admin)
):
    """Tải về file đính kèm gốc của tài liệu nếu có"""
    doc = db.query(InternalDoc).filter(InternalDoc.id == doc_id).first()
    if not doc or not doc.file_path or not os.path.exists(doc.file_path):
        raise HTTPException(status_code=404, detail="File gốc không tồn tại trên hệ thống")

    return FileResponse(
        path=doc.file_path,
        filename=doc.filename or f"doc_{doc_id}.pdf",
        media_type="application/octet-stream"
    )

@router.post("/docs", response_model=InternalDocOut)
def create_internal_doc(
    doc_in: InternalDocCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff_or_admin)
):
    doc = InternalDoc(**doc_in.dict())
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc

@router.put("/docs/{doc_id}", response_model=InternalDocOut)
def update_internal_doc(
    doc_id: int,
    doc_in: InternalDocUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff_or_admin)
):
    doc = db.query(InternalDoc).filter(InternalDoc.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài liệu")

    for field, val in doc_in.dict(exclude_unset=True).items():
        if val is not None:
            setattr(doc, field, val)

    db.commit()
    db.refresh(doc)
    return doc

@router.delete("/docs/{doc_id}")
def delete_internal_doc(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff_or_admin)
):
    doc = db.query(InternalDoc).filter(InternalDoc.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài liệu")
    
    # Remove physical file if exists
    if doc.file_path and os.path.exists(doc.file_path):
        try:
            os.remove(doc.file_path)
        except Exception:
            pass

    db.delete(doc)
    db.commit()
    return {"message": "Đã xóa tài liệu khỏi Vector DB thành công", "doc_id": doc_id}

@router.delete("/spaces/{space_name}")
def clear_vector_space(
    space_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff_or_admin)
):
    """Xóa toàn bộ tài liệu trong một Không gian Vector (Vector Space) cụ thể"""
    deleted_count = db.query(InternalDoc).filter(InternalDoc.category == space_name).delete()
    db.commit()
    return {"message": f"Đã xóa sạch không gian '{space_name}' ({deleted_count} tài liệu)", "deleted_count": deleted_count}

@router.post("/reset-sample-docs")
def reset_sample_docs(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff_or_admin)
):
    """Khôi phục/Nạp lại các tài liệu mẫu chuẩn GearVN vào Vector DB"""
    db.query(InternalDoc).delete()
    db.commit()

    for item in SAMPLE_DOCS:
        doc = InternalDoc(**item)
        db.add(doc)
    db.commit()

    return {"message": "Đã khôi phục thành công các tài liệu mẫu vào Vector DB!", "total_docs": len(SAMPLE_DOCS)}
