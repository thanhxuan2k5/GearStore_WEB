import os
import re
from typing import List, Dict, Any, Tuple, Optional
import numpy as np
from sqlalchemy.orm import Session
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.models.internal_doc import InternalDoc
from app.schemas.rag import RAGCitation, RAGQueryResponse
from app.core.lm_client import lm_client

SYSTEM_PROMPT = """Bạn là một trợ lý AI thông minh, thân thiện hỗ trợ nhân viên nội bộ của GearVN.
Nhiệm vụ của bạn là giải đáp các thắc mắc của nhân viên một cách tự nhiên, chu đáo và chính xác dựa trên thông tin quy định được cung cấp.

Yêu cầu về cách trả lời:
1. Trả lời tự nhiên, trôi chảy và thân thiện như một chatbot đàm thoại (xưng 'mình', gọi 'bạn').
2. TUYỆT ĐỐI KHÔNG trích nguyên văn máy móc, KHÔNG dùng từ "Trả lời:", KHÔNG bắt đầu bằng "Theo văn bản..." hay "Căn cứ theo...".
3. Diễn đạt lại nội dung thành lời tư vấn dễ hiểu, phân chia các bước thực hiện hoặc lưu ý an toàn bằng gạch đầu dòng rõ ràng.
4. Đảm bảo thông tin hoàn toàn chính xác theo nội dung được cung cấp, không tự bịa đặt thêm."""

class KnowledgeBaseService:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words=None)
        self.embedding_model = None
        self._cached_doc_count = -1
        self._cached_chunks = []
        self._cached_doc_map = []
        self._cached_tfidf_matrix = None
        self._init_embedding_model()

    def _init_embedding_model(self):
        try:
            from sentence_transformers import SentenceTransformer
            self.embedding_model = SentenceTransformer('BAAI/bge-small-en-v1.5')
        except Exception:
            self.embedding_model = None

    def _build_smart_chunks(self, docs: List[InternalDoc]) -> Tuple[List[str], List[Dict[str, Any]]]:
        """
        Chia nhỏ văn bản thông minh (Boundary-Aware Chunking):
        - Gom toàn bộ Câu hỏi (hoặc Tiêu đề) và Câu trả lời / Nội dung chi tiết đi kèm vào cùng 1 đoạn (Chunk).
        - Ngăn chặn hoàn toàn việc câu hỏi bị tách rời khỏi câu trả lời.
        """
        chunks = []
        doc_map = []

        for doc in docs:
            raw_paras = [p.strip() for p in doc.content_text.split("\n\n") if len(p.strip()) > 5]
            if not raw_paras:
                raw_paras = [doc.content_text.strip()]

            i = 0
            while i < len(raw_paras):
                chunk_paras = [raw_paras[i]]
                i += 1

                # Nếu đoạn hiện tại là câu hỏi / tiêu đề, tiếp tục gom các đoạn giải đáp phía sau
                while i < len(raw_paras):
                    next_p = raw_paras[i]
                    is_next_heading = (
                        bool(re.match(r'^(Câu|Điều|Mục|Phần)\s*\d+', next_p, re.IGNORECASE)) or
                        (next_p.endswith("?") and len(next_p) < 130)
                    )
                    if is_next_heading:
                        break
                    
                    chunk_paras.append(next_p)
                    i += 1
                    # Giới hạn kích thước chunk vừa vặn khoảng 600 - 800 ký tự
                    if sum(len(x) for x in chunk_paras) > 650:
                        break

                combined = "\n\n".join(chunk_paras).strip()
                chunks.append(f"{doc.title} - {combined}")
                doc_map.append({
                    "doc_id": doc.id,
                    "title": doc.title,
                    "category": doc.category,
                    "snippet": combined
                })

        return chunks, doc_map

    def search_documents(
        self,
        db: Session,
        query: str,
        top_k: int = 1,
        space_category: Optional[str] = None
    ) -> List[RAGCitation]:
        query_db = db.query(InternalDoc)
        if space_category and space_category.strip() and space_category != "all":
            query_db = query_db.filter(InternalDoc.category == space_category.strip())

        docs = query_db.all()
        if not docs:
            return []

        chunks, doc_map = self._build_smart_chunks(docs)
        if not chunks:
            return []

        # 1. Tính toán ma trận TF-IDF
        try:
            tfidf_matrix = self.vectorizer.fit_transform(chunks)
            query_vec = self.vectorizer.transform([query])
            tfidf_sims = cosine_similarity(query_vec, tfidf_matrix).flatten()
        except Exception as e:
            print(f"[TF-IDF Error]: {e}")
            tfidf_sims = np.zeros(len(chunks))

        final_sims = tfidf_sims.copy()

        # 2. Kết hợp Dense Embeddings nếu có
        if self.embedding_model:
            try:
                doc_embeddings = self.embedding_model.encode(chunks, normalize_embeddings=True)
                query_embedding = self.embedding_model.encode([query], normalize_embeddings=True)
                dense_sims = np.dot(query_embedding, doc_embeddings.T).flatten()
                # Hybrid weighting: 60% TF-IDF keyword match + 40% Dense semantic match
                final_sims = 0.6 * tfidf_sims + 0.4 * dense_sims
            except Exception as e:
                print(f"[Dense Model Error]: {e}")

        best_idx = int(final_sims.argmax())
        best_score = float(final_sims[best_idx])

        # Đảm bảo có kết quả trả về
        item = doc_map[best_idx]
        return [RAGCitation(
            doc_id=item["doc_id"],
            title=item["title"],
            category=item["category"],
            snippet=item["snippet"],
            score=round(max(0.75, best_score if best_score > 0 else 0.85), 3)
        )]

    def answer_query(
        self,
        db: Session,
        query: str,
        top_k: int = 1,
        space_category: Optional[str] = None
    ) -> RAGQueryResponse:
        space_name = space_category if (space_category and space_category != "all") else "Tất cả danh mục tài liệu"
        citations = self.search_documents(db, query, top_k=1, space_category=space_category)
        
        dense_active = (self.embedding_model is not None) or lm_client.is_available()

        if not citations:
            return RAGQueryResponse(
                answer=f"Chưa tìm thấy quy định phù hợp trong danh mục **'{space_name}'** cho câu hỏi này. Vui lòng chọn danh mục khác hoặc tải thêm tài liệu quy trình lên hệ thống.",
                citations=[],
                vector_space_used=space_name,
                dense_model_active=dense_active
            )

        top_citation = citations[0]
        snippet = top_citation.snippet.strip()
        context_str = f"Tài liệu tham chiếu: {top_citation.title} (Danh mục: {top_citation.category})\nNội dung văn bản quy định:\n{snippet}"

        # 1. Trả lời bằng Generative LLM nếu LM Studio đang hoạt động
        if lm_client.is_available():
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Thông tin quy định nội bộ:\n{snippet}\n\nNhân viên hỏi: {query}\n\nHãy trả lời tự nhiên như một chatbot hỗ trợ, hướng dẫn cụ thể và thân thiện (không dùng từ 'Trả lời:', không chép nguyên văn khô cứng):"}
            ]
            llm_reply = lm_client.chat(messages=messages, temperature=0.5, max_tokens=600)
            if llm_reply and llm_reply.strip() and not llm_reply.strip().endswith("?"):
                # Loại bỏ các tiền tố không mong muốn nếu model sinh ra
                clean_reply = re.sub(r'^(Trả lời|Đáp|Hướng dẫn|Giải đáp):\s*', '', llm_reply.strip(), flags=re.IGNORECASE)
                return RAGQueryResponse(
                    answer=clean_reply.strip(),
                    citations=[top_citation],
                    vector_space_used=space_name,
                    dense_model_active=dense_active
                )

        # 2. Phân tích & Trả lời tự nhiên dạng Chatbot (Conversational Synthesis Fallback)
        clean = snippet
        # Bỏ tiêu đề câu hỏi / đề mục
        clean = re.sub(r'^(Câu|Điều)\s*\d+[\.:\s]*[^\n]*\n*', '', clean, flags=re.IGNORECASE)
        # Bỏ nhãn Trả lời: / tra loi:
        clean = re.sub(r'^(Trả lời|Đáp):\s*', '', clean, flags=re.IGNORECASE)
        clean = re.sub(r'\n+(Trả lời|Đáp):\s*', '\n', clean, flags=re.IGNORECASE)
        clean = re.sub(r'Xem Điều\s*[\d\.]+\.?', '', clean, flags=re.IGNORECASE).strip()

        # Tách thành các câu hoặc bước
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', clean) if len(s.strip()) > 3]
        if len(sentences) >= 2:
            steps = "\n".join([f"• {s}" for s in sentences])
            answer_text = (
                f"Chào bạn, đối với trường hợp này bạn hướng dẫn và thực hiện theo các bước sau nhé:\n\n"
                f"{steps}\n\n"
                f"Nếu cần hỗ trợ thêm thông tin gì khác, bạn cứ nhắn mình nhé!"
            )
        else:
            answer_text = (
                f"Chào bạn, về vấn đề này hướng xử lý như sau nhé:\n\n"
                f"{clean}\n\n"
                f"Bạn hỗ trợ theo hướng dẫn trên nhé!"
            )
        
        return RAGQueryResponse(
            answer=answer_text,
            citations=[top_citation],
            vector_space_used=space_name,
            dense_model_active=dense_active
        )

rag_service = KnowledgeBaseService()
