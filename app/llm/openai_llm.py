"""
OpenAI LLM实现
"""
import json
import logging
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI

from app.models import SchemaField, ExtractedValue
from app.core import LLMException, settings
from .base import BaseLLM

logger = logging.getLogger(__name__)


class OpenAILLM(BaseLLM):
    """OpenAI LLM实现"""
    
    def __init__(self):
        """初始化OpenAI客户端"""
        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
        )
    
    async def extract(
        self,
        content: str,
        image: Optional[bytes],
        schema: List[SchemaField],
        model: str,
    ) -> List[ExtractedValue]:
        """
        使用OpenAI提取数据
        
        Args:
            content: 文件内容
            schema: 数据schema
            model: 模型名称
            
        Returns:
            提取的数据列表
        """
        try:
            # 构建优化的prompt
            prompt = self._build_prompt(content, schema)
            
            logger.info(f"开始调用OpenAI API，模型: {model}")
            
            # 调用OpenAI API（支持多模态图像）
            if image:
                import base64
                import magic
                mime_type = magic.from_buffer(image, mime=True)
                image_base64 = base64.b64encode(image).decode("utf-8")
                image_url = f"data:{mime_type};base64,{image_base64}"
                response = await self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": self._get_system_prompt()},
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {"type": "image_url", "image_url": {"url": image_url}},
                            ],
                        },
                    ],
                    temperature=0,
                    max_tokens=4096,
                )
            else:
                response = await self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": self._get_system_prompt()},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0,
                    response_format={"type": "json_object"},
                )
            
            # 提取响应内容
            response_text = response.choices[0].message.content or ""
            
            logger.info("OpenAI API调用成功")
            
            # 解析响应
            return self._parse_response(response_text, schema)
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析错误: {str(e)}")
            raise LLMException(f"LLM响应JSON解析失败: {str(e)}")
        except Exception as e:
            logger.error(f"OpenAI API调用失败: {str(e)}")
            raise LLMException(f"OpenAI API调用失败: {str(e)}")
    
    def _get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """你是一个专业的数据提取助手。你的任务是从给定的文本内容中，
根据提供的schema定义，准确地提取相关信息并以JSON格式返回。

重要要求：
1. 仅提取schema中定义的字段
2. 严格按照指定的字段类型进行类型转换
3. 如果字段标记为required且内容中找不到相关信息，则设置为null
4. 对于日期字段，使用ISO 8601格式(YYYY-MM-DD或YYYY-MM-DD HH:mm:ss)
5. 布尔值必须是true或false
6. 数值字段保持数值类型，不要转换为字符串
7. 如果字段值不存在或为空，返回null而不是空字符串
8. 返回的JSON数组中每个对象都必须包含field、type和value三个字段
9. 确保JSON格式完整有效
"""
    
    def _build_prompt(
        self,
        content: str,
        schema: List[SchemaField],
        image: Optional[bytes] = None,
    ) -> str:
        """
        构建优化的Prompt
        
        采用Few-shot学习和清晰的指令设计：
        1. 清晰的任务描述
        2. Schema定义
        3. 文本内容
        4. 输出格式示例
        
        Args:
            content: 文件内容
            schema: 数据schema
            
        Returns:
            优化的Prompt文本
        """
        # 构建schema JSON
        schema_json = json.dumps(
            [
                {
                    "name": field.name,
                    "field": field.field,
                    "type": field.type,
                    "required": field.required,
                }
                for field in schema
            ],
            ensure_ascii=False,
            indent=2,
        )
        
        # 构建输出格式示例
        output_example = json.dumps(
            [
                {
                    "field": field.field,
                    "type": field.type,
                    "value": self._get_example_value(field.type),
                }
                for field in schema
            ],
            ensure_ascii=False,
            indent=2,
        )
        
        prompt = f"""请从以下文本内容中提取信息，并按照指定的schema返回JSON数据。

【Schema定义】
{schema_json}

【待提取的文本内容】
{content}

【输出格式要求】
返回一个JSON数组，每个对象包含field、type和value三个字段。示例：
{output_example}

【特别说明】
- 仅提取schema中定义的字段
- 严格按照指定的字段类型进行类型转换
- 如果字段为必填但内容中找不到相关信息，设置为null
- 日期字段使用ISO 8601格式
- 布尔值使用true/false
- 数值保持数值类型
- 返回有效的JSON数组

请直接返回JSON数组，不要添加其他说明文字。"""
        
        return prompt
    
    def _get_example_value(self, field_type: str) -> Any:
        """根据字段类型获取示例值"""
        examples = {
            "text": "示例文本值",
            "int": 123,
            "float": 123.45,
            "boolean": True,
            "date": "2024-01-01",
            "datetime": "2024-01-01 12:00:00",
        }
        return examples.get(field_type, "示例值")
    
    def _parse_response(
        self,
        response: str,
        schema: List[SchemaField],
    ) -> List[ExtractedValue]:
        """
        解析LLM响应
        
        Args:
            response: LLM响应文本
            schema: 数据schema
            
        Returns:
            提取的数据列表
        """
        try:
            # 解析JSON响应
            response_data = json.loads(response)
            
            # 如果不是列表，包装为列表
            if not isinstance(response_data, list):
                response_data = [response_data]
            
            # 构建schema字段字典以便验证
            schema_dict = {field.field: field for field in schema}
            
            # 转换为ExtractedValue列表
            extracted_values = []
            for item in response_data:
                if not isinstance(item, dict):
                    continue
                
                field_name = item.get("field")
                field_type = item.get("type")
                value = item.get("value")
                
                # 验证字段是否在schema中
                if field_name not in schema_dict:
                    logger.warning(f"字段 {field_name} 不在schema中，跳过")
                    continue
                
                # 类型转换和验证
                field_type_str = str(field_type) if field_type is not None else "text"
                converted_value = self._convert_value(value, field_type_str)
                
                extracted_values.append(
                    ExtractedValue(
                        field=field_name,
                        type=field_type_str,
                        value=converted_value,
                    )
                )
            
            logger.info(f"成功解析{len(extracted_values)}个字段")
            return extracted_values
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {str(e)}")
            raise LLMException(f"无法解析LLM响应: {str(e)}")
    
    def _convert_value(self, value: Any, field_type: str) -> Any:
        """
        根据字段类型转换值
        
        Args:
            value: 原始值
            field_type: 字段类型
            
        Returns:
            转换后的值
        """
        if value is None:
            return None
        
        try:
            if field_type == "int":
                return int(value)
            elif field_type == "float":
                return float(value)
            elif field_type == "boolean":
                if isinstance(value, bool):
                    return value
                if isinstance(value, str):
                    return value.lower() in ("true", "yes", "1")
                return bool(value)
            elif field_type in ("date", "datetime"):
                return str(value)
            else:  # text
                return str(value)
        except (ValueError, TypeError) as e:
            logger.warning(f"类型转换失败: {value} -> {field_type}: {str(e)}")
            return str(value)
