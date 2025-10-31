"""
提取服务 - 业务逻辑层
"""
import logging
import os
from typing import List, Optional, Union

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
        image_bytes: Optional[bytes] = None

        # 2. 判别是否为图像文件；若为图像，跳过OCR，直接走LLM视觉
        logger.info("步骤2: 判别文件类型并准备多模态输入")
        detected_ext = None
        try:
            detected_ext = self.file_service.detect_file_type(file_content, request.filename)
        except Exception:
            detected_ext = None

        is_image = bool(detected_ext and detected_ext.lower() in self.file_service.IMAGE_TYPES)

        if is_image:
            logger.info(f"检测到图像类型: {detected_ext}，跳过OCR，直接使用LLM视觉能力")
            text_content = ""
            image_bytes = file_content
        else:
            logger.info("非图像文件，提取文本内容供LLM使用")
            text_content = await self._extract_text(
                request.source,
                request.file,
                file_content,
                request.filename,
            )
        
        # 3. 使用LLM提取数据
        logger.info("步骤3: 使用LLM提取数据")
        extracted_data = await self._extract_with_llm(
            text_content=text_content,
            image=image_bytes,
            schema=request.fields,
            provider=request.provider,
            model=request.model,
        )
        
        logger.info(f"数据提取完成，共提取{len(extracted_data)}个字段")
        return extracted_data
    
    async def _get_file_content(self, source: str, file_data: Union[str, bytes]) -> bytes:
        """
        获取文件内容
        
        Args:
            source: 文件来源 ("minio" 或 "raw")
            file_data: 文件路径/URL（用于minio）或文本/二进制数据（用于raw）
            
        Returns:
            文件内容字节
        """
        if source == "minio":
            logger.info(f"从MinIO下载文件: {file_data}")
            return await self.minio_service.download_file(str(file_data))
        elif source == "file":
            # raw数据可能是字符串或二进制，需要转换为字节
            if isinstance(file_data, bytes):
                return file_data
            else:
                return str(file_data).encode("utf-8")
        else:
            raise ValidationException(f"不支持的文件来源: {source}")
    
    async def _extract_text(
        self,
        source: str,
        file_data: Union[str, bytes],
        file_content: bytes,
        filename: Optional[str] = None,
    ) -> str:
        """
        从文件提取文本
        
        Args:
            source: 文件来源
            file_data: 文件路径/URL或文本/二进制数据
            file_content: 文件内容字节
            filename: 原始文件名（可选，用于自动判断文件类型）
            
        Returns:
            提取的文本内容
        """
        # 从MinIO URL获取文件扩展名
        extension = self.file_service._get_file_extension(str(file_data))
        return await self.file_service.extract_text_from_file(
            file_content,
            extension,
            filename,
        )
    
    async def _extract_with_llm(
        self,
        text_content: str,
        image: Optional[bytes],
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
            content=text_content,
            image=image,
            schema=schema,
            model=model or "default",
        )
