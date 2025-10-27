"""
提取API路由
"""
import logging
import json
from fastapi import APIRouter, HTTPException, status, Form, File, UploadFile
from typing import Optional, List

from app.models import ExtractRequest, ExtractResponse, ErrorResponse, SchemaField
from app.core import AppException
from app.services import ExtractService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["extract"])

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
async def extract(
    source: str = Form(..., description="文件来源: 'minio' 或 'file'"),
    url: Optional[str] = Form(None, description="MinIO URL"),
    schema_str: str = Form(..., alias="schema", description="JSON格式的Schema字段定义数组"),
    provider: str = Form("openai", description="LLM提供商: openai|azure|claude|gemini|custom"),
    model: Optional[str] = Form(None, description="LLM模型名称（可选）"),
    file: Optional[UploadFile] = File(None, description="上传的文件"),
) -> ExtractResponse:
    """
    数据提取端点
    
    ### 请求参数（FormData）
    - **source**: 文件来源，"minio"或"file"（必需）
    - **url**: MinIO URL
    - **file**: 上传的文件
    - **schema**: JSON格式的Schema字段定义数组（必需）
    - **provider**: LLM提供商，"openai"|"azure"|"claude"|"gemini"|"custom"（默认: openai）
    - **model**: LLM模型名称（可选）
    
    ### 返回
    包含提取数据的JSON响应
    
    ### 示例
    
    **使用 cURL (FormData):**
    ```bash
    curl -X POST http://localhost:8000/extract \\
      -F "source=file" \\
      -F "file=张三是一名程序员，出生于1990年5月15日" \\
      -F 'schema=[{"name":"人名","field":"name","type":"text","required":true}]' \\
      -F "provider=openai" \\
      -F "model=gpt-4o-mini"
    ```
    
    **使用 Custom 提供商:**
    ```bash
    # 首先设置环境变量
    export CUSTOM_BASE_URL=https://chat.ecnu.edu.cn/open/api/v1
    export CUSTOM_API_KEY=sk-xxxxxxxxxxxx
    
    # 然后发送请求（无需在请求中传递 custom_base_url 和 custom_api_key）
    curl -X POST http://localhost:8000/extract \\
      -F "source=raw" \\
      -F "file=华为是中国领先的科技公司" \\
      -F 'schema=[{"name":"公司","field":"company","type":"text"}]' \\
      -F "provider=custom" \\
      -F "model=gpt-3.5-turbo"
    ```
    """
    try:
        logger.info(f"收到提取请求: source={source}, provider={provider}")
        if source == "file":
            if not file:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail={
                        "code": "INVALID_INPUT",
                        "message": "必须提供 file 参数",
                    },
                )
        
            # 如果上传了文件，读取其内容
            file_bytes = await file.read()
            upload_filename = file.filename
    
            # 尝试解码为文本，如果失败则保留原始字节
            try:
                if isinstance(file_bytes, bytes):
                    file_content = file_bytes.decode("utf-8")
                    logger.info(f"读取上传文件（文本）: {upload_filename}")
                else:
                    file_content = file_bytes
                    logger.info(f"读取上传文件（二进制）: {upload_filename}")
            except UnicodeDecodeError:
                # 如果是二进制文件（如PDF、图片等），保留原始内容
                # 后续交给 FileProcessingService 处理
                file_content = file_bytes
                logger.info(f"读取上传文件（二进制）: {upload_filename}")
        elif source == "minio":
            if not url:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail={
                        "code": "INVALID_INPUT",
                        "message": "必须提供 url 参数",
                    },
                )
            upload_filename = ""
            file_bytes = url
        else:
            raise ValueError("source 应为 file 或 minio")

        # 解析 schema JSON 字符串
        try:
            schema_list = json.loads(schema_str)
            if not isinstance(schema_list, list):
                raise ValueError("schema 必须是数组")
            
            # 转换为 SchemaField 对象
            schema_fields = [SchemaField(**item) for item in schema_list]
        except json.JSONDecodeError as e:
            logger.error(f"Schema JSON 解析失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "code": "INVALID_SCHEMA",
                    "message": f"Schema JSON 格式无效: {str(e)}",
                },
            )
        except (ValueError, TypeError) as e:
            logger.error(f"Schema 字段转换失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "code": "INVALID_SCHEMA",
                    "message": f"Schema 字段定义无效: {str(e)}",
                },
            )
        
        # 创建请求对象
        request = ExtractRequest(
            source=source,  # type: ignore
            file=file_content,  # type: ignore
            schema=schema_fields,
            provider=provider,  # type: ignore
            model=model,
            filename=upload_filename,
        )
        
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
