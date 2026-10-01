import json
from typing import List, Dict, Any, Optional
import requests
from app.config import settings

class LocalLLMClient:
    """
    Client kết nối tới Local LLM Server (LM Studio, Ollama hoặc vLLM)
    theo chuẩn giao thức OpenAI API (/v1/chat/completions)
    """
    def __init__(self):
        self.base_url = settings.LM_STUDIO_URL.rstrip('/')
        self.default_model = settings.LM_STUDIO_MODEL
        self.timeout = 15 # seconds

    def is_server_online(self) -> bool:
        """Kiểm tra xem LM Studio Server có đang bật không"""
        try:
            res = requests.get(f"{self.base_url}/models", timeout=2)
            return res.status_code == 200
        except Exception:
            return False

    def generate_chat_response(
        self,
        system_prompt: str,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 800
    ) -> Optional[str]:
        """Gửi prompt tới LM Studio và nhận về câu trả lời tự nhiên"""
        if not settings.USE_LOCAL_LLM:
            return None

        messages = [{"role": "system", "content": system_prompt}]
        
        if conversation_history:
            for msg in conversation_history[-4:]: # Lấy 4 tin nhắn gần nhất để giữ ngữ cảnh
                messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})

        messages.append({"role": "user", "content": user_message})

        payload = {
            "model": self.default_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=self.timeout
            )
            if response.status_code == 200:
                data = response.json()
                return data["choices"][0]["message"]["content"]
            else:
                print(f"[LM Studio Warning] HTTP {response.status_code}: {response.text}")
                return None
        except Exception as e:
            # Server LM Studio chưa bật hoặc bị lỗi timeout -> Graceful fallback
            return None

local_llm = LocalLLMClient()
