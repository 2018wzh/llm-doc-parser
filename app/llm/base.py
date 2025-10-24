"""
LLM基础接口定义
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from app.models import SchemaField, ExtractedValue


class BaseLLM(ABC):
    """LLM基础接口"""
    
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
