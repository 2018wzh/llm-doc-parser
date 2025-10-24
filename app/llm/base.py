"""
LLM基础接口定义 - 支持多平台多模型
"""
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel

from app.models import SchemaField, ExtractedValue

logger = logging.getLogger(__name__)


class ModelCapability(str, Enum):
    """模型能力枚举"""
    TEXT = "text"                          # 文本处理
    JSON_MODE = "json_mode"                # JSON 模式
    VISION = "vision"                      # 图像理解
    FUNCTION_CALLING = "function_calling"  # 函数调用
    STREAMING = "streaming"                # 流式输出
    LONG_CONTEXT = "long_context"          # 长上下文


class ModelInfo(BaseModel):
    """模型信息"""
    name: str                               # 模型名称
    display_name: str                       # 显示名称
    provider: str                           # 提供商
    description: Optional[str] = None       # 描述
    max_tokens: Optional[int] = None        # 最大 token
    capabilities: List[str] = []            # 能力列表
    cost_per_1k_input: Optional[float] = None  # 输入成本
    cost_per_1k_output: Optional[float] = None  # 输出成本


class BaseLLM(ABC):
    """LLM基础接口 - 支持多平台多模型"""
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """提供商名称"""
        pass
    
    @abstractmethod
    async def extract(
        self,
        content: str,
        schema: List[SchemaField],
        model: str,
    ) -> List[ExtractedValue]:
        """
        根据schema和内容提取数据
        
        Args:
            content: 文件内容
            schema: 数据schema
            model: 模型名称
            
        Returns:
            提取的数据列表
        """
        pass
    
    @abstractmethod
    def _build_prompt(
        self,
        content: str,
        schema: List[SchemaField],
    ) -> str:
        """
        构建优化的Prompt
        
        Args:
            content: 文件内容
            schema: 数据schema
            
        Returns:
            优化的Prompt文本
        """
        pass
    
    @abstractmethod
    def _parse_response(
        self,
        response: str,
        schema: List[SchemaField],
    ) -> List[ExtractedValue]:
        """
        解析LLM响应
        
        Args:
            response: LLM响应文本
            schema: 数据schema
            
        Returns:
            提取的数据列表
        """
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[ModelInfo]:
        """
        获取可用模型列表
        
        Returns:
            模型信息列表
        """
        pass
    
    @abstractmethod
    async def validate_connection(self) -> bool:
        """
        验证连接是否正常
        
        Returns:
            连接状态
        """
        pass
    
    def _convert_value(self, value: Any, field_type: str) -> Any:
        """
        根据字段类型转换值
        
        Args:
            value: 原始值
            field_type: 字段类型
            
        Returns:
            转换后的值
        """
        if value is None:
            return None
        
        try:
            if field_type == "int":
                return int(value)
            elif field_type == "float":
                return float(value)
            elif field_type == "boolean":
                if isinstance(value, bool):
                    return value
                if isinstance(value, str):
                    return value.lower() in ("true", "yes", "1")
                return bool(value)
            elif field_type in ("date", "datetime"):
                return str(value)
            else:  # text
                return str(value)
        except (ValueError, TypeError) as e:
            logger.warning(f"类型转换失败: {value} -> {field_type}: {str(e)}")
            return str(value)
