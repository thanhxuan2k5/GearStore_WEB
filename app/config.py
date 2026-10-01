import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "GearVN Tech Store & AI Assistant"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "gearvn_super_secret_jwt_key_2026_xyz_!@#"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days
    
    # Database (Default SQLite for portability, easily switch to PostgreSQL)
    DATABASE_URL: str = "sqlite:///./data/gearvn.db"
    
    # Paths
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR: str = os.path.join(BASE_DIR, "data")
    CSV_SALES_PATH: str = os.path.join(DATA_DIR, "sales_realtime.csv")
    INTERNAL_DOCS_DIR: str = os.path.join(DATA_DIR, "internal_docs")
    UPLOADS_DIR: str = os.path.join(DATA_DIR, "uploads")
    
    # AI & Local LLM Settings
    USE_LOCAL_LLM: bool = True
    LM_STUDIO_URL: str = "http://127.0.0.1:1234/v1"
    LM_STUDIO_MODEL: str = "qwen2.5-7b-instruct"
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    # LM Studio — Local LLM (OpenAI-compatible API)
    # Khởi động LM Studio, load model, server sẽ chạy tại localhost:1234
    LM_STUDIO_URL: str = os.getenv("LM_STUDIO_URL", "http://localhost:1234/v1")
    LM_STUDIO_MODEL: str = os.getenv("LM_STUDIO_MODEL", "local-model")
    LM_STUDIO_API_KEY: str = os.getenv("LM_STUDIO_API_KEY", "")
    LM_STUDIO_ENABLED: bool = os.getenv("LM_STUDIO_ENABLED", "true").lower() == "true"
    LM_STUDIO_TIMEOUT: int = int(os.getenv("LM_STUDIO_TIMEOUT", "30"))

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()

os.makedirs(settings.DATA_DIR, exist_ok=True)
os.makedirs(settings.INTERNAL_DOCS_DIR, exist_ok=True)
os.makedirs(settings.UPLOADS_DIR, exist_ok=True)
