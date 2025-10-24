"""
LLM工厂模式实现
"""
import logging
from typing import Dict, Type

from app.core import LLMException
from .base import BaseLLM
from .openai_llm import OpenAILLM

logger = logging.getLogger(__name__)


class LLMFactory:
    """LLM工厂类 - 用于创建LLM实例"""
    
    # 支持的LLM提供商
    _providers: Dict[str, Type[BaseLLM]] = {
        "openai": OpenAILLM,
    }
    
    @classmethod
    def create(cls, provider: str = "openai") -> BaseLLM:
        """
        创建LLM实例
        
        Args:
            provider: LLM提供商（目前仅支持openai）
            
        Returns:
            LLM实例
            
        Raises:
            LLMException: 如果提供商不支持
        """
        provider = provider.lower()
        
        if provider not in cls._providers:
            raise LLMException(
                f"不支持的LLM提供商: {provider}。"
                f"支持的提供商: {', '.join(cls._providers.keys())}"
            )
        
        logger.info(f"创建{provider}提供商的LLM实例")
        
        llm_class = cls._providers[provider]
        return llm_class()
    
    @classmethod
    def register(cls, provider: str, llm_class: Type[BaseLLM]) -> None:
        """
        注册新的LLM提供商
        
        Args:
            provider: 提供商名称
            llm_class: LLM类
        """
        if not issubclass(llm_class, BaseLLM):
            raise TypeError(f"{llm_class} 必须继承自 BaseLLM")
        
        cls._providers[provider.lower()] = llm_class
        logger.info(f"已注册LLM提供商: {provider}")
    
    @classmethod
    def get_supported_providers(cls) -> list:
        """获取支持的LLM提供商列表"""
        return list(cls._providers.keys())
