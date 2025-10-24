"""
MinIO文件服务
"""
import logging
from typing import Optional
from minio import Minio
from minio.error import S3Error
import io

from app.core import MinIOException, settings

logger = logging.getLogger(__name__)


class MinIOService:
    """MinIO文件服务"""
    
    def __init__(self):
        """初始化MinIO客户端"""
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )
    
    async def download_file(self, url: str) -> bytes:
        """
        从MinIO下载文件
        
        Args:
            url: MinIO文件URL，格式: http://endpoint/bucket/object-name
            
        Returns:
            文件内容字节
            
        Raises:
            MinIOException: 文件下载失败
        """
        try:
            # 解析URL获取bucket和object_name
            bucket_name, object_name = self._parse_url(url)
            
            logger.info(f"开始从MinIO下载文件: {bucket_name}/{object_name}")
            
            # 下载文件
            response = self.client.get_object(bucket_name, object_name)
            file_content = response.read()
            response.close()
            
            logger.info(f"文件下载成功，大小: {len(file_content)} 字节")
            return file_content
            
        except S3Error as e:
            logger.error(f"MinIO S3错误: {str(e)}")
            raise MinIOException(f"MinIO操作失败: {str(e)}")
        except Exception as e:
            logger.error(f"文件下载失败: {str(e)}")
            raise MinIOException(f"文件下载失败: {str(e)}")
    
    def _parse_url(self, url: str) -> tuple:
        """
        解析MinIO URL获取bucket和object_name
        
        支持格式：
        - http://endpoint/bucket/object-name
        - bucket/object-name
        
        Args:
            url: MinIO URL或路径
            
        Returns:
            (bucket_name, object_name)
            
        Raises:
            MinIOException: URL格式不正确
        """
        try:
            if url.startswith("http://") or url.startswith("https://"):
                # 从完整URL解析
                # http://endpoint/bucket/object-name
                parts = url.split("/")
                if len(parts) < 4:
                    raise ValueError("URL格式不正确")
                bucket_name = parts[3]
                object_name = "/".join(parts[4:])
            else:
                # 从路径解析
                # bucket/object-name
                parts = url.split("/", 1)
                if len(parts) != 2:
                    raise ValueError("路径格式不正确")
                bucket_name, object_name = parts
            
            if not bucket_name or not object_name:
                raise ValueError("Bucket或Object名称为空")
            
            return bucket_name, object_name
            
        except Exception as e:
            logger.error(f"URL解析失败: {str(e)}")
            raise MinIOException(f"MinIO URL格式不正确: {url}")
