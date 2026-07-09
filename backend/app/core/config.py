import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    APP_NAME: str = "AI Workbench"
    VERSION: str = "1.0.0"
    DEBUG: bool = True

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://root:Root@123456@localhost:3306/ai_workbench"
    )
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    SECRET_KEY: str = os.getenv("SECRET_KEY", "ai-workbench-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    QWEN_MODEL_NAME: str = os.getenv("QWEN_MODEL_NAME", "Qwen/Qwen2.5-1.5B-Instruct")
    EMBEDDING_MODEL_NAME: str = os.getenv("EMBEDDING_MODEL_NAME", "BAAI/bge-small-zh-v1.5")
    MODEL_DEVICE: str = os.getenv("MODEL_DEVICE", "cpu")
    VECTOR_PATH: str = os.getenv("VECTOR_PATH", "./chroma_db")

    RATE_LIMIT_PER_MINUTE: int = 60
    SESSION_CACHE_TTL: int = 3600

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
