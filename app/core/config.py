"""
应用配置文件
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用全局配置"""
    
    # FastAPI配置
    APP_TITLE: str = "LLM Document Parser"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # OpenAI配置
    OPENAI_API_KEY: str
    OPENAI_BASE_URL: Optional[str] = None
    
    # MinIO配置
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    MINIO_SECURE: bool = False
    
    # 应用配置
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    ALLOWED_FILE_TYPES: list = [
        "pdf", "docx", "doc", "txt", "xlsx", "xls", "pptx", "ppt"
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
