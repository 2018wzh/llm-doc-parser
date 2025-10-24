"""
提取API路由
"""
import logging
from fastapi import APIRouter, HTTPException, status

from app.models import ExtractRequest, ExtractResponse, ErrorResponse
from app.core import AppException
from app.services import ExtractService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["extract"])

# 创建服务实例
extract_service = ExtractService()


@router.post(
    "/extract",
    response_model=ExtractResponse,
    responses={
        422: {"model": ErrorResponse, "description": "验证失败或文件处理失败"},
        500: {"model": ErrorResponse, "description": "服务器错误"},
    },
    summary="数据提取",
    description="从文件（MinIO或原始文本）根据指定字段schema提取数据",
)
async def extract(request: ExtractRequest) -> ExtractResponse:
    """
    数据提取端点
    
    ### 请求参数
    - **source**: 文件来源，"minio"或"raw"
    - **file**: minIO URL或者原始文本内容
    - **schema** (或字段名): 数据库中查到的schema
    - **provider**: LLM提供商，"openai"|"azure"|"claude"|"gemini"|"custom"（默认: openai）
    - **model**: LLM模型名称（若不指定则使用默认值）
    
    ### 返回
    包含提取数据的JSON响应
    
    ### 示例
    ```json
    POST /api/v1/extract
    {
        "source": "raw",
        "file": "张三是一名程序员，出生于1990年5月15日",
        "provider": "openai",
        "model": "gpt-4o-mini",
        "schema": [
            {
                "name": "人名",
                "field": "name",
                "type": "text",
                "required": true
            },
            {
                "name": "职业",
                "field": "occupation",
                "type": "text",
                "required": true
            },
            {
                "name": "出生日期",
                "field": "birth_date",
                "type": "date",
                "required": true
            }
        ]
    }
    ```
    """
    try:
        logger.info(f"收到提取请求: source={request.source}")
        
        # 调用服务执行提取
        extracted_data = await extract_service.extract(request)
        
        # 返回成功响应
        return ExtractResponse(
            data=extracted_data,
            code="200",
            message="Success",
        )
        
    except AppException as e:
        logger.warning(f"应用异常: {e.code} - {e.message}")
        raise HTTPException(
            status_code=e.status_code,
            detail={
                "code": e.code,
                "message": e.message,
            },
        )
    except Exception as e:
        logger.error(f"未预期的错误: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "服务器内部错误",
            },
        )
