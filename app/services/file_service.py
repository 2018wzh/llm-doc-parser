"""
文件处理服务
"""
import logging
from typing import Optional
from pathlib import Path
import tempfile
import os
import io
import magic

from PIL import Image
import pytesseract

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
    
    # MIME 类型映射到文件扩展名
    MIME_TYPE_MAP = {
        "application/pdf": "pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
        "application/msword": "doc",
        "text/plain": "txt",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "xlsx",
        "application/vnd.ms-excel": "xls",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation": "pptx",
        "application/vnd.ms-powerpoint": "ppt",
        "image/jpeg": "jpg",
        "image/png": "png",
        "image/bmp": "bmp",
        "image/gif": "gif",
        "image/tiff": "tiff",
        "image/webp": "webp",
    }
    
    # 支持的图像类型
    IMAGE_TYPES = {"jpg", "jpeg", "png", "bmp", "gif", "tiff", "webp"}
    
    @staticmethod
    def detect_file_type(
        file_content: bytes,
        filename: Optional[str] = None,
    ) -> Optional[str]:
        """
        自动判断文件类型
        
        Args:
            file_content: 文件内容字节
            filename: 文件名（可选）
            
        Returns:
            文件扩展名（不含点），如 'pdf', 'docx' 等；如无法判断则返回 None
        """
        try:
            mime_type = magic.from_buffer(file_content, mime=True)
            logger.debug(f"检测到 MIME 类型: {mime_type}")
                
            # 从 MIME 类型映射到扩展名
            detected_ext = FileProcessingService.MIME_TYPE_MAP.get(mime_type)
            if detected_ext:
                logger.debug(f"从 MIME 类型映射到文件类型: {detected_ext}")
                return detected_ext
        except Exception as e:
            logger.error(f"文件类型检测异常: {str(e)}")
            return None
    
    @staticmethod
    async def extract_text_from_image(
        file_content: bytes,
        filename: Optional[str] = None,
    ) -> str:
        """
        从图像文件中提取文本（OCR）
        
        使用 Tesseract OCR 进行文本识别
        
        Args:
            file_content: 图像文件内容字节
            filename: 图像文件名（可选）
            
        Returns:
            OCR 提取的文本内容
            
        Raises:
            FileProcessingException: 图像处理失败
        """
        try:
            logger.info(f"开始处理图像文件: {filename or '未命名'}")
            
            # 从字节流打开图像
            try:
                image = Image.open(io.BytesIO(file_content))
                logger.debug(f"图像信息 - 格式: {image.format}, 大小: {image.size}")
            except Exception as e:
                logger.error(f"图像打开失败: {str(e)}")
                raise FileProcessingException(f"无效的图像文件: {str(e)}")
            
            # 使用 Tesseract 进行文本识别
            try:
                logger.info("开始 Tesseract OCR 识别...")
                
                # Tesseract 直接识别 PIL Image 对象
                # 使用 lang='chi_sim+eng' 支持中文和英文
                # 如果只需要中文，使用 lang='chi_sim'
                # 如果只需要英文，使用 lang='eng'
                text_content = pytesseract.image_to_string(
                    image,
                    lang='chi_sim+eng',
                    config='--psm 6'  # PSM 6: 假设单个文本块
                )
                
                text_content = text_content.strip()
                
                if not text_content:
                    logger.warning("OCR 识别未找到文本内容")
                    text_content = "(图像中未检测到文本内容)"
                else:
                    logger.info(f"OCR 识别成功，提取文本长度: {len(text_content)} 字符")
                
                return text_content
                
            except Exception as e:
                logger.error(f"OCR 识别失败: {str(e)}")
                raise FileProcessingException(f"图像 OCR 识别失败: {str(e)}")
            
        except FileProcessingException:
            raise
        except Exception as e:
            logger.error(f"图像处理异常: {str(e)}")
            raise FileProcessingException(f"图像处理失败: {str(e)}")
    
    
    @staticmethod
    async def extract_text_from_file(
        file_content: bytes,
        file_extension: Optional[str] = None,
        filename: Optional[str] = None,
    ) -> str:
        """
        从文件内容中提取文本
        
        支持多种文件格式：
        - 文档格式 (PDF, Word, Excel, PowerPoint 等)
        - 纯文本格式 (TXT)
        - 图像格式 (PNG, JPG, BMP, GIF, TIFF, WebP) - 自动进行 OCR
        
        Args:
            file_content: 文件内容字节
            file_extension: 文件扩展名（可选，如果不提供会自动检测）
            filename: 原始文件名（可选，用于自动判断文件类型）
            
        Returns:
            提取的文本内容
            
        Raises:
            FileProcessingException: 文件处理失败
        """
        try:
            logger.info("开始处理文件")
            
            # 如果未提供扩展名，尝试自动判断
            detected_extension = file_extension
            if not detected_extension:
                detected_extension = FileProcessingService.detect_file_type(
                    file_content,
                    filename
                )
                if detected_extension:
                    logger.info(f"自动检测到文件类型: {detected_extension}")
            
            # 检查是否为图像文件
            if detected_extension and detected_extension.lower() in FileProcessingService.IMAGE_TYPES:
                logger.info(f"检测到图像文件类型: {detected_extension}，使用 OCR 处理")
                return await FileProcessingService.extract_text_from_image(
                    file_content,
                    filename
                )
            
            # 处理其他文件格式（文档、文本等）
            # 创建临时文件
            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=f".{detected_extension}" if detected_extension else "",
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
