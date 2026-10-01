import sys
import os
import httpx

# Fix Windows console UTF-8 encoding
if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')

from app.config import settings
from app.core.lm_client import lm_client

def test_connection():
    print("=" * 60)
    print("[*] DANG KIEM TRA KET NOI TOI LM STUDIO...")
    print(f"[*] URL cau hinh: {settings.LM_STUDIO_URL}")
    print("=" * 60)

    # 1. Ping LM Studio Server
    headers = {}
    if settings.LM_STUDIO_API_KEY:
        headers["Authorization"] = f"Bearer {settings.LM_STUDIO_API_KEY}"

    try:
        resp = httpx.get(f"{settings.LM_STUDIO_URL}/models", headers=headers, timeout=3.0)
        if resp.status_code == 200:
            print("[OK] 1. Ket noi Server LM Studio: THANH CONG (Port 1234 dang hoat dong)")
            models = resp.json().get("data", [])
            print(f"     -> Danh sach model dang load: {[m.get('id') for m in models]}")
        elif resp.status_code == 401:
            print("[WARN] 1. LM Studio Server yeu cau API Token.")
            print("       -> Cach 1: Trong LM Studio, tab Local Server -> Gạt tắt mục 'Require API Key / Authentication'.")
            print("       -> Cach 2: Hoac copy token tren LM Studio va dan vao file .env: LM_STUDIO_API_KEY=your_token")
        else:
            print(f"[WARN] 1. Server phan hoi ma loi HTTP {resp.status_code}")
    except Exception as e:
        print("[FAIL] 1. Ket noi that bai: Ban chua bam 'Start Server' tren LM Studio hoac sai Port 1234.")
        print("       (Hay mo LM Studio, vao tab Local Server va bam nut Start Server)")
        return

    # 2. Test chat thử nghiệm với Qwen 2.5
    print("\n[*] 2. Dang gui thu tin nhan test toi model Qwen 2.5...")
    test_msg = [{"role": "user", "content": "Chao ban, hay gioi thieu ngan gon trong 1 cau ban la ai."}]
    reply = lm_client.chat(messages=test_msg, max_tokens=100)
    
    if reply:
        print("[OK] 2. Phan hoi tu Qwen 2.5 thanh cong:")
        print(f"     -> \"{reply.strip()}\"")
        print("\n>>> CHUC MUNG! HE THONG DA TICH HOP LM STUDIO THANH CONG 100%! <<<")
    else:
        print("[NOTE] Neu chua nhan duoc phan hoi, hay kiem tra:")
        print("       1. Da bam nút 'Start Server' trong LM Studio.")
        print("       2. Neu LM Studio co bat 'Require API Key', hay tat no hoac dien vao .env.")

if __name__ == "__main__":
    test_connection()
