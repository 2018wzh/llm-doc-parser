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
    
    # LLM 提供商选择（openai|azure|claude|gemini）
    LLM_PROVIDER: str = "openai"
    
    # OpenAI配置
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_BASE_URL: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    
    # Azure OpenAI配置
    AZURE_OPENAI_KEY: Optional[str] = None
    AZURE_OPENAI_ENDPOINT: Optional[str] = None
    AZURE_OPENAI_API_VERSION: Optional[str] = "2024-02-15-preview"
    AZURE_OPENAI_DEPLOYMENT: Optional[str] = None
    
    # Anthropic Claude配置
    ANTHROPIC_API_KEY: Optional[str] = None
    CLAUDE_MODEL: str = "claude-3-sonnet-20240229"
    
    # Google Gemini配置
    GOOGLE_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-2.0-flash"
    
    # Custom (OpenAI兼容) 配置
    CUSTOM_BASE_URL: Optional[str] = None
    CUSTOM_API_KEY: Optional[str] = None
    CUSTOM_MODEL: str = "gpt-3.5-turbo"
    
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
    
    def validate_llm_provider(self) -> None:
        """验证LLM提供商配置"""
        provider = self.LLM_PROVIDER.lower()
        
        if provider == "openai":
            if not self.OPENAI_API_KEY:
                raise ValueError("使用OpenAI时必须设置OPENAI_API_KEY")
        
        elif provider == "azure":
            required_fields = [
                "AZURE_OPENAI_KEY",
                "AZURE_OPENAI_ENDPOINT",
                "AZURE_OPENAI_DEPLOYMENT",
            ]
            for field in required_fields:
                if not getattr(self, field):
                    raise ValueError(f"使用Azure OpenAI时必须设置{field}")
        
        elif provider == "claude":
            if not self.ANTHROPIC_API_KEY:
                raise ValueError("使用Claude时必须设置ANTHROPIC_API_KEY")
        
        elif provider == "gemini":
            if not self.GOOGLE_API_KEY:
                raise ValueError("使用Gemini时必须设置GOOGLE_API_KEY")
        
        elif provider == "custom":
            if not self.CUSTOM_BASE_URL:
                raise ValueError("使用Custom提供商时必须设置CUSTOM_BASE_URL")
        
        else:
            raise ValueError(
                f"不支持的LLM提供商: {provider}。"
                f"支持的提供商: openai, azure, claude, gemini, custom"
            )


settings = Settings()

# 验证配置
try:
    settings.validate_llm_provider()
except ValueError as e:
    import logging
    logger = logging.getLogger(__name__)
    logger.warning(f"LLM配置警告: {str(e)}")

