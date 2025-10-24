"""
图像处理服务单元测试
"""
import pytest
import asyncio
from pathlib import Path
from PIL import Image
import io

from app.services.file_service import FileProcessingService
from app.core import FileProcessingException


class TestImageTypeDetection:
    """图像类型检测测试"""
    
    def test_detect_png_image(self):
        """测试 PNG 图像检测"""
        # 创建简单的 PNG 图像
        img = Image.new('RGB', (100, 100), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        file_type = FileProcessingService.detect_file_type(
            img_bytes.read(),
            filename="test.png"
        )
        assert file_type == "png"
    
    def test_detect_jpg_image(self):
        """测试 JPG 图像检测"""
        img = Image.new('RGB', (100, 100), color='blue')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        file_type = FileProcessingService.detect_file_type(
            img_bytes.read(),
            filename="test.jpg"
        )
        assert file_type in ["jpg", "jpeg"]
    
    def test_detect_bmp_image(self):
        """测试 BMP 图像检测"""
        img = Image.new('RGB', (100, 100), color='green')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='BMP')
        img_bytes.seek(0)
        
        file_type = FileProcessingService.detect_file_type(
            img_bytes.read(),
            filename="test.bmp"
        )
        assert file_type == "bmp"
    
    def test_image_types_constant(self):
        """测试图像类型常量"""
        assert "png" in FileProcessingService.IMAGE_TYPES
        assert "jpg" in FileProcessingService.IMAGE_TYPES
        assert "jpeg" in FileProcessingService.IMAGE_TYPES
        assert "bmp" in FileProcessingService.IMAGE_TYPES
        assert "gif" in FileProcessingService.IMAGE_TYPES
        assert "tiff" in FileProcessingService.IMAGE_TYPES
        assert "webp" in FileProcessingService.IMAGE_TYPES


class TestImageProcessing:
    """图像处理测试"""
    
    @pytest.mark.asyncio
    async def test_extract_text_from_png_image(self):
        """测试从 PNG 图像提取文本"""
        # 创建一个简单的图像
        img = Image.new('RGB', (200, 100), color='white')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        # 测试图像处理
        try:
            text = await FileProcessingService.extract_text_from_image(
                img_bytes.read(),
                filename="test.png"
            )
            # 空白图像应该返回 "未检测到文本" 的提示
            assert isinstance(text, str)
            assert len(text) > 0
        except FileProcessingException as e:
            # 也可能抛出异常，取决于 OCR 实现
            assert "OCR" in str(e) or "图像" in str(e)
    
    @pytest.mark.asyncio
    async def test_extract_text_from_invalid_image(self):
        """测试处理无效的图像文件"""
        invalid_data = b"not an image"
        
        with pytest.raises(FileProcessingException):
            await FileProcessingService.extract_text_from_image(
                invalid_data,
                filename="invalid.png"
            )


class TestFileExtensionDetection:
    """文件扩展名检测测试"""
    
    def test_get_file_extension_from_url(self):
        """测试从 URL 获取文件扩展名"""
        ext = FileProcessingService._get_file_extension(
            "http://example.com/images/photo.png"
        )
        assert ext == "png"
    
    def test_get_file_extension_from_path(self):
        """测试从路径获取文件扩展名"""
        ext = FileProcessingService._get_file_extension(
            "/home/user/images/photo.jpg"
        )
        assert ext == "jpg"
    
    def test_get_file_extension_uppercase(self):
        """测试大写扩展名"""
        ext = FileProcessingService._get_file_extension(
            "photo.PNG"
        )
        assert ext == "png"
    
    def test_get_file_extension_no_extension(self):
        """测试没有扩展名的文件"""
        ext = FileProcessingService._get_file_extension(
            "photo"
        )
        assert ext is None


class TestMimeTypeMapping:
    """MIME 类型映射测试"""
    
    def test_image_mime_types_in_map(self):
        """测试图像 MIME 类型在映射中"""
        mime_map = FileProcessingService.MIME_TYPE_MAP
        
        assert mime_map.get("image/jpeg") in ["jpg", "jpeg"]
        assert mime_map.get("image/png") == "png"
        assert mime_map.get("image/bmp") == "bmp"
        assert mime_map.get("image/gif") == "gif"
        assert mime_map.get("image/tiff") == "tiff"
        assert mime_map.get("image/webp") == "webp"
    
    def test_document_mime_types_preserved(self):
        """测试文档 MIME 类型保留"""
        mime_map = FileProcessingService.MIME_TYPE_MAP
        
        assert mime_map.get("application/pdf") == "pdf"
        assert mime_map.get("text/plain") == "txt"


class TestIntegration:
    """集成测试"""
    
    @pytest.mark.asyncio
    async def test_file_type_routing(self):
        """测试文件类型路由 - 图像文件应该使用 OCR"""
        # 创建 PNG 图像
        img = Image.new('RGB', (100, 100), color='white')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        # 测试自动路由到 OCR 处理
        text = await FileProcessingService.extract_text_from_file(
            img_bytes.read(),
            filename="test.png"
        )
        
        assert isinstance(text, str)
        assert len(text) > 0
    
    def test_supported_types_and_image_types_no_overlap(self):
        """测试支持的类型和图像类型没有重叠"""
        doc_types = set()
        for types in FileProcessingService.SUPPORTED_TYPES.values():
            doc_types.update(types)
        
        image_types = FileProcessingService.IMAGE_TYPES
        
        # 应该没有重叠
        overlap = doc_types & image_types
        assert len(overlap) == 0, f"类型重叠: {overlap}"


# 性能测试
class TestPerformance:
    """性能相关测试"""
    
    def test_ocr_engine_singleton(self):
        """测试 OCR 引擎单例模式"""
        from app.services.file_service import _get_ocr_engine
        
        engine1 = _get_ocr_engine()
        engine2 = _get_ocr_engine()
        
        # 应该是同一个实例
        assert engine1 is engine2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
