"""
AI Sales Assistant — Hybrid Rule-based + LM Studio
===================================================
Kiến trúc 2 tầng:
  Tầng 1: SQLAlchemy DB query để tìm sản phẩm phù hợp (rule-based, GIỮA NGUYÊN)
  Tầng 2: LM Studio để viết câu trả lời tự nhiên (MỚI)

Fallback: Nếu LM Studio không chạy → dùng reply template cũ (không crash)
"""
import re
import json
from typing import List, Dict, Any, Optional, Tuple

from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.product import Product
from app.schemas.ai import AIChatRequest, AIChatResponse, RecommendedProductItem
from app.core.lm_client import lm_client


# ------------------------------------------------------------------
# System Prompt cho LM Studio
# Điều chỉnh tại đây để thay đổi phong cách tư vấn của AI
# ------------------------------------------------------------------
SALES_SYSTEM_PROMPT = """Bạn là Trợ lý AI GearVN — chuyên gia tư vấn thiết bị công nghệ hàng đầu Việt Nam.

Vai trò: Tư vấn sản phẩm công nghệ (laptop, PC, linh kiện, phụ kiện gaming) dựa trên nhu cầu khách hàng.

Phong cách giao tiếp:
- Luôn dùng tiếng Việt tự nhiên, thân thiện
- Xưng "em", gọi khách là "bạn"
- Giải thích thông số kỹ thuật bằng ngôn ngữ dễ hiểu (tránh jargon thuần túy)
- Nhiệt tình, chuyên nghiệp, không cứng nhắc

Quy tắc TƯ VẤN:
1. Phân tích nhu cầu thực sự của khách (gaming/đồ họa/văn phòng/học tập/AI)
2. Chỉ gợi ý sản phẩm từ danh sách được hệ thống cung cấp — KHÔNG bịa sản phẩm
3. Giải thích lý do cụ thể tại sao mỗi sản phẩm phù hợp với nhu cầu
4. Nếu có lịch sử hội thoại, hãy đọc hiểu và tiếp nối ngữ cảnh
5. Đề xuất câu hỏi gợi ý để khách hiểu thêm về sản phẩm

Format phản hồi:
- Chào hỏi ngắn gọn
- Phân tích nhu cầu (1-2 câu)
- Giới thiệu từng sản phẩm kèm link markdown [Tên sản phẩm](/product/slug)
- Kết thúc bằng lời mời hỏi thêm"""


class AISalesAssistant:

    # ------------------------------------------------------------------
    # Budget Extraction (giữ nguyên)
    # ------------------------------------------------------------------

    def extract_budget(self, text: str) -> Optional[float]:
        """Trích xuất ngân sách từ câu nói tự nhiên của người dùng."""
        text = text.lower()
        # Patterns: "20 triệu", "20tr", "20.5 triệu", "hai mươi triệu"
        m = re.search(r'(\d+(?:[\.,]\d+)?)\s*(?:triệu|tr|củ)', text)
        if m:
            val_str = m.group(1).replace(',', '.')
            try:
                return float(val_str) * 1_000_000
            except ValueError:
                pass
        # Pattern: "20,000,000" hoặc "20.000.000"
        m2 = re.search(r'(\d{1,3}(?:\.\d{3}){2,3})', text)
        if m2:
            try:
                return float(m2.group(1).replace('.', ''))
            except ValueError:
                pass
        return None

    # ------------------------------------------------------------------
    # DB Query Logic (giữ nguyên — rule-based nhưng chính xác)
    # ------------------------------------------------------------------

    def _query_products(
        self,
        db: Session,
        lower_msg: str,
        extracted_budget: Optional[float]
    ) -> List[Product]:
        """Tìm sản phẩm phù hợp từ DB dựa trên keyword + budget."""
        # Keyword mapping: category detection
        category_keywords = {
            "laptop":   ["laptop", "máy tính xách tay", "macbook", "notebook"],
            "pc":       ["pc", "máy bàn", "cây máy tính", "case", "dàn máy"],
            "vga":      ["card màn hình", "vga", "rtx", "gtx", "rx"],
            "monitor":  ["màn hình", "monitor", "display"],
            "keyboard": ["bàn phím", "bàn phím cơ", "keyboard"],
            "mouse":    ["chuột", "mouse", "chuột không dây"],
        }

        target_cat = None
        for cat_key, words in category_keywords.items():
            if any(w in lower_msg for w in words):
                target_cat = cat_key
                break

        query = db.query(Product)

        # Filter theo budget (15% tolerance — có thể điều chỉnh)
        if extracted_budget:
            query = query.filter(Product.promo_price <= extracted_budget * 1.15)

        # Filter theo category
        if target_cat == "laptop":
            query = query.filter(or_(
                Product.name.ilike("%Laptop%"),
                Product.slug.ilike("%laptop%")
            ))
        elif target_cat == "pc":
            query = query.filter(or_(
                Product.name.ilike("%PC%"),
                Product.slug.ilike("%pc%"),
                Product.name.ilike("%Bộ máy tính%")
            ))
        elif target_cat == "vga":
            query = query.filter(or_(
                Product.name.ilike("%VGA%"),
                Product.name.ilike("%Card%"),
                Product.pc_part_type == "vga"
            ))
        elif target_cat == "monitor":
            query = query.filter(or_(
                Product.name.ilike("%Màn hình%"),
                Product.pc_part_type == "monitor"
            ))
        elif target_cat == "keyboard":
            query = query.filter(Product.name.ilike("%Bàn phím%"))
        elif target_cat == "mouse":
            query = query.filter(Product.name.ilike("%Chuột%"))

        # Sắp xếp: rating cao + bán nhiều trước
        products = query.order_by(
            Product.rating_avg.desc(),
            Product.sales_count.desc()
        ).limit(5).all()  # Lấy 5 để LLM có context phong phú hơn

        # Fallback nếu không tìm được
        if not products:
            products = db.query(Product).order_by(
                Product.is_featured.desc(),
                Product.sales_count.desc()
            ).limit(5).all()

        return products

    def _build_recommended_items(self, products: List[Product]) -> List[RecommendedProductItem]:
        """Chuyển Product ORM objects sang RecommendedProductItem schema."""
        items = []
        for p in products:
            specs = {}
            try:
                specs = json.loads(p.specs_json) if p.specs_json else {}
            except Exception:
                pass
            items.append(RecommendedProductItem(
                id=p.id,
                name=p.name,
                slug=p.slug,
                brand=p.brand,
                promo_price=p.promo_price,
                original_price=p.original_price,
                thumbnail=p.thumbnail,
                specs=specs,
                reason="",  # LLM sẽ generate reason trong reply
            ))
        return items

    # ------------------------------------------------------------------
    # LM Studio — Reply Generation (MỚI)
    # ------------------------------------------------------------------

    def _build_products_context(self, items: List[RecommendedProductItem]) -> str:
        """Tạo context string để inject vào LLM prompt."""
        if not items:
            return "Không tìm thấy sản phẩm phù hợp."
        lines = []
        for i, item in enumerate(items, 1):
            specs_str = ", ".join([f"{k}: {v}" for k, v in item.specs.items()]) if item.specs else "Chưa có thông số"
            savings = int(item.original_price - item.promo_price)
            lines.append(
                f"{i}. {item.name} (slug: {item.slug})\n"
                f"   Thương hiệu: {item.brand}\n"
                f"   Giá KM: {int(item.promo_price):,}đ | Giá gốc: {int(item.original_price):,}đ"
                + (f" | Tiết kiệm: {savings:,}đ" if savings > 0 else "") + "\n"
                f"   Thông số: {specs_str}"
            )
        return "\n\n".join(lines)

    def _generate_llm_reply(
        self,
        request: AIChatRequest,
        items: List[RecommendedProductItem]
    ) -> Optional[str]:
        """
        Gọi LM Studio để tạo câu trả lời tư vấn tự nhiên.

        Tham số LLM có thể điều chỉnh:
        - temperature=0.65 : Tự nhiên, sáng tạo nhưng nhất quán
        - max_tokens=900   : Đủ cho tư vấn 3 sản phẩm chi tiết
        - top_p=0.92       : Nucleus sampling, lọc bỏ tokens xác suất thấp
        """
        products_context = self._build_products_context(items)

        # Xây dựng messages — GIỜ DÙNG conversation_history THẬT SỰ
        messages: List[Dict[str, str]] = [
            {"role": "system", "content": SALES_SYSTEM_PROMPT}
        ]

        # Inject lịch sử hội thoại (schema đã có từ trước, giờ mới dùng)
        for hist_msg in (request.conversation_history or []):
            if hist_msg.role in ["user", "assistant", "system"]:
                messages.append({"role": hist_msg.role, "content": hist_msg.content})

        # Message hiện tại kèm context sản phẩm
        messages.append({
            "role": "user",
            "content": (
                f"Yêu cầu của khách hàng: {request.message}\n\n"
                f"Sản phẩm hệ thống đề xuất (dựa trên DB GearVN):\n"
                f"{products_context}\n\n"
                f"Hãy tư vấn cho khách hàng, dùng link markdown cho tên sản phẩm."
            )
        })

        return lm_client.chat(
            messages=messages,
            temperature=0.65,   # Điều chỉnh: 0.3 (nhất quán) ↔ 0.9 (sáng tạo)
            max_tokens=900,     # Điều chỉnh theo độ dài mong muốn
            top_p=0.92,
        )

    # ------------------------------------------------------------------
    # Fallback reply (giữ nguyên từ code cũ khi LM Studio offline)
    # ------------------------------------------------------------------

    def _generate_fallback_reply(
        self,
        items: List[RecommendedProductItem],
        extracted_budget: Optional[float]
    ) -> str:
        budget_str = f"{int(extracted_budget):,}đ" if extracted_budget else "linh hoạt"
        parts = [
            f"Dạ chào bạn! Em là **Trợ lý AI GearVN**.",
            f"Theo nhu cầu của bạn (Ngân sách: **{budget_str}**), "
            f"em đề xuất các sản phẩm sau:"
        ]
        for idx, item in enumerate(items[:3], 1):
            savings = int(item.original_price - item.promo_price)
            parts.append(
                f"\n**{idx}. [{item.name}](/product/{item.slug})**\n"
                f"- Giá: **{int(item.promo_price):,}đ**"
                + (f" (Tiết kiệm: *{savings:,}đ*)" if savings > 0 else "")
            )
        parts.append("\n👉 Click vào sản phẩm để xem chi tiết hoặc hỏi thêm nhé!")
        return "\n".join(parts)

    @staticmethod
    def _get_suggested_questions(lower_msg: str) -> List[str]:
        """Câu hỏi gợi ý động dựa trên nội dung câu hỏi."""
        base = [
            "So sánh hiệu năng giữa các sản phẩm được gợi ý",
            "Chính sách bảo hành và trả góp như thế nào?",
        ]
        if "game" in lower_msg or "gaming" in lower_msg:
            base.insert(0, "Cấu hình này có chơi mượt Black Myth: Wukong không?")
            base.append("Tư vấn cấu hình PC Gaming trong tầm giá 25 triệu")
        elif "đồ họa" in lower_msg or "render" in lower_msg:
            base.insert(0, "Màn hình nào phù hợp để làm đồ họa chuyên nghiệp?")
        elif "sinh viên" in lower_msg or "văn phòng" in lower_msg:
            base.insert(0, "Laptop nào pin trâu nhất trong tầm giá?")
        return base[:4]

    # ------------------------------------------------------------------
    # Entry point chính
    # ------------------------------------------------------------------

    def process_consultation(self, db: Session, request: AIChatRequest) -> AIChatResponse:
        user_msg = request.message.strip()
        lower_msg = user_msg.lower()

        # Bước 1: Extract budget
        extracted_budget = request.budget or self.extract_budget(user_msg)

        # Bước 2: DB Query lấy sản phẩm (rule-based, không thay đổi)
        products = self._query_products(db, lower_msg, extracted_budget)
        recommended_items = self._build_recommended_items(products)
        # Chỉ trả về tối đa 3 trong response
        display_items = recommended_items[:3]

        # Bước 3: Thử LM Studio reply
        llm_reply = self._generate_llm_reply(request, display_items)

        # Bước 4: Fallback nếu LM Studio offline
        final_reply = llm_reply or self._generate_fallback_reply(display_items, extracted_budget)

        return AIChatResponse(
            reply=final_reply,
            intent="consultation",
            recommended_products=display_items,
            suggested_questions=self._get_suggested_questions(lower_msg),
        )


ai_sales_assistant = AISalesAssistant()
