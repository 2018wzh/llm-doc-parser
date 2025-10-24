"""
提取服务 - 业务逻辑层
"""
import logging
import os
from typing import List, Optional

from app.models import ExtractRequest, ExtractedValue, SchemaField
from app.core import ValidationException
from app.llm import LLMFactory
from .minio_service import MinIOService
from .file_service import FileProcessingService

logger = logging.getLogger(__name__)


class ExtractService:
    """数据提取服务 - 协调各个服务完成数据提取"""
    
    def __init__(self):
        """初始化服务"""
        self.minio_service = MinIOService()
        self.file_service = FileProcessingService()
    
    async def extract(self, request: ExtractRequest) -> List[ExtractedValue]:
        """
        执行数据提取
        
        Args:
            request: 提取请求
            
        Returns:
            提取的数据列表
            
        Raises:
            ValidationException: 验证失败
            其他异常: 处理过程中的异常
        """
        logger.info(f"开始数据提取: source={request.source}, provider={request.provider}, model={request.model}")
        
        # 1. 获取文件内容
        logger.info("步骤1: 获取文件内容")
        file_content = await self._get_file_content(request.source, request.file)
        
        # 2. 提取文本
        logger.info("步骤2: 从文件提取文本")
        text_content = await self._extract_text(request.source, request.file, file_content)
        
        # 3. 使用LLM提取数据
        logger.info("步骤3: 使用LLM提取数据")
        extracted_data = await self._extract_with_llm(
            text_content,
            request.fields,
            request.provider,
            request.model,
        )
        
        logger.info(f"数据提取完成，共提取{len(extracted_data)}个字段")
        return extracted_data
    
    async def _get_file_content(self, source: str, file_path: str) -> bytes:
        """
        获取文件内容
        
        Args:
            source: 文件来源 ("minio" 或 "raw")
            file_path: 文件路径或URL
            
        Returns:
            文件内容字节
        """
        if source == "minio":
            logger.info(f"从MinIO下载文件: {file_path}")
            return await self.minio_service.download_file(file_path)
        elif source == "raw":
            # raw文本不需要下载，直接处理
            return file_path.encode("utf-8")
        else:
            raise ValidationException(f"不支持的文件来源: {source}")
    
    async def _extract_text(
        self,
        source: str,
        file_path: str,
        file_content: bytes,
    ) -> str:
        """
        从文件提取文本
        
        Args:
            source: 文件来源
            file_path: 文件路径或URL
            file_content: 文件内容字节
            
        Returns:
            提取的文本内容
        """
        if source == "raw":
            # raw文本直接处理
            text = file_content.decode("utf-8")
            return await self.file_service.extract_text_from_raw(text)
        elif source == "minio":
            # 从MinIO URL获取文件扩展名
            extension = self.file_service._get_file_extension(file_path)
            return await self.file_service.extract_text_from_file(
                file_content,
                extension,
            )
        else:
            raise ValidationException(f"不支持的文件来源: {source}")
    
    async def _extract_with_llm(
        self,
        text_content: str,
        schema: List[SchemaField],
        provider: str,
        model: Optional[str] = None,
    ) -> List[ExtractedValue]:
        """
        使用LLM提取数据
        
        Args:
            text_content: 文本内容
            schema: 数据schema
            provider: LLM提供商 (openai|azure|claude|gemini|custom)
            model: 模型名称（若不指定则使用默认值）
            
        Returns:
            提取的数据列表
        """
        # 为 custom 提供商构建参数
        kwargs = {}
        if provider.lower() == "custom":
            # 从环境变量获取 custom 提供商的配置
            base_url = os.getenv("CUSTOM_BASE_URL")
            if not base_url:
                raise ValidationException("使用 custom 提供商时必须设置环境变量 CUSTOM_BASE_URL")
            kwargs["base_url"] = base_url
            
            api_key = os.getenv("CUSTOM_API_KEY")
            if api_key:
                kwargs["api_key"] = api_key
            
            if model:
                kwargs["model_name"] = model
        
        # 使用工厂模式创建LLM实例
        llm = LLMFactory.create(provider, **kwargs)
        
        # 使用LLM提取数据
        return await llm.extract(
            text_content,
            schema,
            model or "default",
        )
