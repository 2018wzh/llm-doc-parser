"""
数据模型定义
"""
from typing import List, Literal, Optional, Any
from pydantic import BaseModel, Field, field_validator


class SchemaField(BaseModel):
    """Schema字段定义"""
    name: str = Field(..., description="字段详情")
    field: str = Field(..., description="字段名称")
    type: Literal["text", "int", "float", "boolean", "date", "datetime"] = Field(
        ..., description="字段类型"
    )
    required: bool = Field(default=True, description="字段是否必填")


class ExtractRequest(BaseModel):
    """提取请求"""
    source: Literal["minio", "raw"] = Field(..., description="文件来源")
    file: str = Field(..., description="minIO URL或者原始文本内容")
    fields: List[SchemaField] = Field(..., alias="schema", description="数据库中查到的schema")
    provider: Literal["openai", "azure", "claude", "gemini", "custom"] = Field(
        default="openai", description="LLM提供商"
    )
    model: Optional[str] = Field(None, description="LLM模型名称（若不指定则使用默认值）")
    # Custom 提供商特定参数
    custom_base_url: Optional[str] = Field(None, description="Custom LLM的API基础URL")
    custom_api_key: Optional[str] = Field(None, description="Custom LLM的API密钥（可选）")


class ExtractedValue(BaseModel):
    """提取的值"""
    field: str = Field(..., description="字段名称")
    type: str = Field(..., description="字段类型")
    value: Optional[Any] = Field(None, description="字段值")


class ExtractResponse(BaseModel):
    """提取响应"""
    data: List[ExtractedValue] = Field(..., description="提取的数据")
    code: str = Field("200", description="状态码")
    message: str = Field("Success", description="消息")


class ErrorResponse(BaseModel):
    """错误响应"""
    code: str = Field(..., description="错误代码")
    message: str = Field(..., description="错误消息")
