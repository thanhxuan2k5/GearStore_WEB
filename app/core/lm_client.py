"""
LM Studio Client — Singleton kết nối tới Local LLM
===================================================
LM Studio expose một OpenAI-compatible API tại http://localhost:1234/v1
Có thể dùng openai Python SDK trực tiếp, chỉ cần đổi base_url.

Thiết kế:
- Singleton pattern: 1 client dùng chung toàn app
- Graceful fallback: nếu LM Studio không chạy → trả về None
  (code gọi phải tự xử lý None, không bao giờ crash)
- Ping check: kiểm tra trước khi inference
- Hỗ trợ JSON mode cho structured output (sentiment, etc.)
"""
import json
import httpx
from typing import Optional, List, Dict, Any
from openai import OpenAI, APIConnectionError, APITimeoutError

from app.config import settings


class LMStudioClient:
    """
    Singleton client quản lý kết nối tới LM Studio.

    Cách dùng:
        from app.core.lm_client import lm_client

        result = lm_client.chat(
            messages=[{"role": "user", "content": "Xin chào"}],
            temperature=0.7,
            max_tokens=200
        )
        if result:
            # Dùng result (str)
        else:
            # LM Studio không chạy → fallback về logic cũ
    """

    _instance: Optional["LMStudioClient"] = None
    _client: Optional[OpenAI] = None
    _available: Optional[bool] = None  # Cache trạng thái availability

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        # Chỉ khởi tạo OpenAI client 1 lần
        if self._client is None and settings.LM_STUDIO_ENABLED:
            api_key = getattr(settings, "LM_STUDIO_API_KEY", "")
            if not api_key:
                api_key = "lm-studio" # Default token placeholder
            self._client = OpenAI(
                base_url=settings.LM_STUDIO_URL,
                api_key=api_key,
                timeout=settings.LM_STUDIO_TIMEOUT,
            )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def is_available(self) -> bool:
        """
        Ping LM Studio để kiểm tra xem server có đang chạy không.
        Kết quả được cache để tránh ping liên tục.
        Gọi reset_availability() nếu muốn recheck.
        """
        if not settings.LM_STUDIO_ENABLED:
            return False
        if self._available is not None:
            return self._available
        try:
            api_key = getattr(settings, "LM_STUDIO_API_KEY", "") or "lm-studio"
            resp = httpx.get(
                f"{settings.LM_STUDIO_URL}/models",
                timeout=3.0,
                headers={"Authorization": f"Bearer {api_key}"}
            )
            self._available = (resp.status_code == 200)
        except Exception:
            self._available = False
        return self._available

    def reset_availability(self):
        """Reset cache trạng thái — dùng sau khi restart LM Studio."""
        self._available = None

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 800,
        top_p: float = 0.95,
        json_mode: bool = False,
    ) -> Optional[str]:
        """
        Gọi chat completion từ LM Studio.

        Args:
            messages:     List[{"role": "system"|"user"|"assistant", "content": str}]
            temperature:  0.0 (deterministic) → 1.0 (sáng tạo)
                          - RAG / Sentiment: 0.0–0.15
                          - Chatbot tư vấn:  0.5–0.7
                          - Insight text:    0.3–0.5
            max_tokens:   Giới hạn độ dài output
                          - JSON output:     60–150
                          - Câu trả lời:     400–1000
            top_p:        Nucleus sampling, thường để 0.85–0.95
            json_mode:    True → yêu cầu model trả về JSON hợp lệ

        Returns:
            str:  Nội dung phản hồi của model
            None: Nếu LM Studio không khả dụng hoặc có lỗi
        """
        if not self._client or not settings.LM_STUDIO_ENABLED:
            return None

        try:
            kwargs: Dict[str, Any] = dict(
                model=settings.LM_STUDIO_MODEL,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                stream=False,
            )
            # JSON mode: một số model hỗ trợ structured output
            if json_mode:
                kwargs["response_format"] = {"type": "json_object"}

            response = self._client.chat.completions.create(**kwargs)
            content = response.choices[0].message.content
            # Reset cache khi thành công
            self._available = True
            return content

        except (APIConnectionError, APITimeoutError):
            print(f"[LMStudio] ⚠️  Không kết nối được tới {settings.LM_STUDIO_URL} "
                  f"— tự động fallback về logic mặc định")
            self._available = False
            return None
        except Exception as e:
            print(f"[LMStudio] ⚠️  Lỗi không xác định: {e} — fallback về logic mặc định")
            return None

    def chat_json(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.0,
        max_tokens: int = 150,
    ) -> Optional[Dict[str, Any]]:
        """
        Gọi chat và parse kết quả JSON tự động.
        Dùng cho Sentiment Classification và các structured output.

        Returns:
            dict: Parsed JSON nếu thành công
            None: Nếu lỗi hoặc không parse được
        """
        raw = self.chat(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            json_mode=True,
        )
        if not raw:
            return None
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            # Thử tìm JSON trong response nếu model thêm text ngoài
            import re
            match = re.search(r'\{.*\}', raw, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except json.JSONDecodeError:
                    pass
    def get_embeddings(self, texts: List[str]) -> Optional[List[List[float]]]:
        """
        Gọi endpoint /v1/embeddings từ LM Studio nếu có load embedding model (bge-small-en).
        
        Returns:
            List[List[float]]: Danh sách vector embeddings nếu thành công
            None: Nếu LM Studio chưa bật endpoint embedding
        """
        if not self._client or not settings.LM_STUDIO_ENABLED:
            return None
        try:
            response = self._client.embeddings.create(
                model="text-embedding-bge-small-en-v1.5",
                input=texts
            )
            return [data.embedding for data in response.data]
        except Exception:
            return None


# Singleton instance — import ở mọi service
lm_client = LMStudioClient()

