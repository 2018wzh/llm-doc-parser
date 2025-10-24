"""
自定义异常定义
"""


class AppException(Exception):
    """应用基础异常"""
    def __init__(self, code: str, message: str, status_code: int = 400):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class MinIOException(AppException):
    """MinIO相关异常"""
    def __init__(self, message: str):
        super().__init__("MINIO_ERROR", message, 500)


class FileProcessingException(AppException):
    """文件处理异常"""
    def __init__(self, message: str):
        super().__init__("FILE_PROCESSING_ERROR", message, 422)


class LLMException(AppException):
    """LLM处理异常"""
    def __init__(self, message: str):
        super().__init__("LLM_ERROR", message, 500)


class ValidationException(AppException):
    """验证异常"""
    def __init__(self, message: str):
        super().__init__("VALIDATION_ERROR", message, 400)
