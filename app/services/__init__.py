"""
服务模块初始化文件
"""
from .minio_service import MinIOService
from .file_service import FileProcessingService
from .extract_service import ExtractService

__all__ = [
    "MinIOService",
    "FileProcessingService",
    "ExtractService",
]
