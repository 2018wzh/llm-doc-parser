"""
LLM工厂模式实现
"""
import logging
from typing import Dict, Type

from app.core import LLMException
from .base import BaseLLM
from .openai_llm import OpenAILLM
from .azure_openai_llm import AzureOpenAILLM
from .claude_llm import ClaudeLLM
from .gemini_llm import GeminiLLM
from .openai_compatible_llm import OpenAICompatibleLLM

logger = logging.getLogger(__name__)


class LLMFactory:
    """LLM工厂类 - 用于创建LLM实例"""
    
    # 支持的LLM提供商
    _providers: Dict[str, Type[BaseLLM]] = {
        "openai": OpenAILLM,
        "azure": AzureOpenAILLM,
        "claude": ClaudeLLM,
        "gemini": GeminiLLM,
        "custom": OpenAICompatibleLLM,
    }
    
    @classmethod
    def create(cls, provider: str = "openai", **kwargs) -> BaseLLM:
        """
        创建LLM实例
        
        Args:
            provider: LLM提供商
            **kwargs: 提供商特定的参数
                - custom 提供商需要: base_url, api_key (可选), model_name (可选)
            
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
        
        # 如果是 custom 提供商，需要传递参数
        if provider == "custom":
            if "base_url" not in kwargs:
                raise LLMException("使用 custom 提供商时必须提供 base_url 参数")
            return llm_class(
                base_url=kwargs["base_url"],
                api_key=kwargs.get("api_key", "not-needed"),
                model_name=kwargs.get("model_name", "gpt-3.5-turbo"),
            )
        
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
