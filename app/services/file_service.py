"""
文件处理服务
"""
import logging
from typing import Optional
from pathlib import Path
import tempfile
import os

from unstructured.partition.auto import partition
from unstructured.partition.text import partition_text

from app.core import FileProcessingException

logger = logging.getLogger(__name__)


class FileProcessingService:
    """文件处理服务 - 使用Unstructured库处理各种文件格式"""
    
    # 支持的文件类型和对应的处理方法
    SUPPORTED_TYPES = {
        "pdf": ["pdf"],
        "docx": ["docx"],
        "doc": ["doc"],
        "txt": ["txt"],
        "xlsx": ["xlsx"],
        "xls": ["xls"],
        "pptx": ["pptx"],
        "ppt": ["ppt"],
    }
    
    @staticmethod
    async def extract_text_from_file(
        file_content: bytes,
        file_extension: Optional[str] = None,
    ) -> str:
        """
        从文件内容中提取文本
        
        Args:
            file_content: 文件内容字节
            file_extension: 文件扩展名（可选，如果不提供会自动检测）
            
        Returns:
            提取的文本内容
            
        Raises:
            FileProcessingException: 文件处理失败
        """
        try:
            logger.info("开始处理文件")
            
            # 创建临时文件
            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=f".{file_extension}" if file_extension else "",
            ) as tmp_file:
                tmp_file.write(file_content)
                tmp_file_path = tmp_file.name
            
            try:
                # 使用Unstructured自动分区
                elements = partition(filename=tmp_file_path)
                
                # 提取文本
                text_content = "\n".join(
                    [str(element) for element in elements if element.text]
                )
                
                logger.info(
                    f"文件处理成功，提取文本长度: {len(text_content)} 字符"
                )
                
                return text_content
                
            finally:
                # 清理临时文件
                if os.path.exists(tmp_file_path):
                    os.remove(tmp_file_path)
                    logger.debug(f"临时文件已删除: {tmp_file_path}")
            
        except Exception as e:
            logger.error(f"文件处理失败: {str(e)}")
            raise FileProcessingException(f"文件处理失败: {str(e)}")
    
    @staticmethod
    async def extract_text_from_raw(raw_text: str) -> str:
        """
        处理原始文本
        
        Args:
            raw_text: 原始文本内容
            
        Returns:
            处理后的文本内容
        """
        if not raw_text or not raw_text.strip():
            raise FileProcessingException("原始文本内容为空")
        
        logger.info(f"处理原始文本，长度: {len(raw_text)} 字符")
        
        return raw_text.strip()
    
    @staticmethod
    def _get_file_extension(url: str) -> Optional[str]:
        """
        从URL获取文件扩展名
        
        Args:
            url: 文件URL
            
        Returns:
            文件扩展名（不含点）
        """
        try:
            path = Path(url)
            suffix = path.suffix.lstrip(".")
            return suffix.lower() if suffix else None
        except Exception:
            return None
