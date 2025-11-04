"""
OpenAI 兼容的 Custom LLM 实现（TOON 输出）

支持任何兼容 OpenAI API 的服务，例如：
- LM Studio 本地服务
- Ollama
- vLLM
- 本地部署的 LLaMA
- 任何兼容 OpenAI 的第三方 API
"""
import json
import logging
from typing import List, Optional

from openai import AsyncOpenAI

from app.models import SchemaField, ExtractedValue
from app.core import LLMException, settings
from .base import BaseLLM, ModelInfo
from app.utils.toon_utils import (
    extract_toon_block,
    toon_decode,
    extract_values_list,
    schema_to_toon,
)

logger = logging.getLogger(__name__)


class OpenAICompatibleLLM(BaseLLM):
    """OpenAI 兼容的 LLM 实现"""
    
    @property
    def provider_name(self) -> str:
        """提供商名称"""
        return "custom"
    
    def __init__(
        self,
        base_url: str,
        api_key: str = "not-needed",
        model_name: str = "gpt-3.5-turbo",
    ):
        """
        初始化 OpenAI 兼容客户端
        
        Args:
            base_url: API 基础 URL（例如：http://localhost:8000/v1）
            api_key: API 密钥（某些本地服务可能不需要）
            model_name: 默认模型名称
        """
        self.base_url = base_url
        self.model_name = model_name
        
        logger.info(f"初始化 OpenAI 兼容客户端: {base_url}")
        
        # 初始化异步客户端
        self.client = AsyncOpenAI(
            base_url=base_url,
            api_key=api_key,
            timeout=60.0,
        )
    
    async def extract(
        self,
        content: str,
        image: Optional[bytes],
        schema: List[SchemaField],
        model: Optional[str] = None,
    ) -> List[ExtractedValue]:
        """使用兼容 OpenAI 的 API 提取数据"""
        try:
            # 使用指定的模型或默认模型
            model_to_use = model or self.model_name
            
            prompt = self._build_prompt(content, schema)
            
            logger.info(f"开始调用 OpenAI 兼容 API，基础 URL: {self.base_url}，模型: {model_to_use}")

            if image:
                import base64
                import magic
                mime_type = magic.from_buffer(image, mime=True)
                image_base64 = base64.b64encode(image).decode('utf-8')
                image_url = f"data:{mime_type};base64,{image_base64}"
                response = await self.client.chat.completions.create(
                    model=model_to_use,
                    messages=[
                        {
                            "role": "system",
                            "content": self._get_system_prompt(),
                        },
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": prompt,
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": image_url,
                                    },
                                }
                            ]
                        },

                    ],
                    temperature=0,
                    max_tokens=4096,
                )
            else:
                response = await self.client.chat.completions.create(
                    model=model_to_use,
                    messages=[
                        {
                            "role": "system",
                            "content": self._get_system_prompt(),
                        },
                        {
                            "role": "user",
                            "content": prompt,
                        },
                    ],
                    temperature=0,
                    max_tokens=4096,
                )
            
            response_text = response.choices[0].message.content or ""
            
            logger.info("OpenAI 兼容 API 调用成功")
            
            return self._parse_response(response_text, schema)
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON 解析错误: {str(e)}")
            raise LLMException(f"LLM 响应 JSON 解析失败: {str(e)}")
        except Exception as e:
            logger.error(f"OpenAI 兼容 API 调用失败: {str(e)}")
            raise LLMException(f"OpenAI 兼容 API 调用失败: {str(e)}")
    
    def get_available_models(self) -> List[ModelInfo]:
        """获取可用模型列表"""
        # 返回一些常见的 OpenAI 兼容模型
        return [
            ModelInfo(
                name="gpt-3.5-turbo",
                display_name="GPT-3.5 Turbo",
                provider="custom",
                description="OpenAI 兼容 - GPT-3.5 Turbo",
                max_tokens=4096,
                capabilities=["text"],
                cost_per_1k_input=0.0015,
                cost_per_1k_output=0.002,
            ),
            ModelInfo(
                name="gpt-4",
                display_name="GPT-4",
                provider="custom",
                description="OpenAI 兼容 - GPT-4",
                max_tokens=8192,
                capabilities=["text"],
                cost_per_1k_input=0.03,
                cost_per_1k_output=0.06,
            ),
            ModelInfo(
                name="llama-2",
                display_name="Llama 2",
                provider="custom",
                description="本地部署的 Llama 2 模型（通过 Ollama 或 LM Studio）",
                max_tokens=4096,
                capabilities=["text"],
                cost_per_1k_input=0.0,
                cost_per_1k_output=0.0,
            ),
            ModelInfo(
                name="mistral",
                display_name="Mistral",
                provider="custom",
                description="本地部署的 Mistral 模型",
                max_tokens=8192,
                capabilities=["text"],
                cost_per_1k_input=0.0,
                cost_per_1k_output=0.0,
            ),
            ModelInfo(
                name="local-model",
                display_name="本地模型",
                provider="custom",
                description="任何本地部署的模型",
                max_tokens=4096,
                capabilities=["text"],
                cost_per_1k_input=0.0,
                cost_per_1k_output=0.0,
            ),
        ]
    
    async def validate_connection(self) -> bool:
        """验证连接"""
        try:
            logger.info(f"验证 OpenAI 兼容 API 连接: {self.base_url}")
            
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "user",
                        "content": "test",
                    }
                ],
                max_tokens=1,
            )
            
            logger.info("OpenAI 兼容 API 连接验证成功")
            return True
            
        except Exception as e:
            logger.error(f"OpenAI 兼容 API 连接验证失败: {str(e)}")
            return False
    
    def _get_system_prompt(self) -> str:
        """获取系统提示词（TOON 输出）"""
        return (
            "你是一个专业的数据提取助手。请根据提供的 schema，从给定内容中提取字段，"
            "并使用 TOON (Token-Oriented Object Notation) 格式返回结果。\n\n"
            "重要要求：\n"
            "1. 仅提取 schema 中定义的字段\n"
            "2. 严格按照指定的字段类型进行类型转换\n"
            "3. 必填字段找不到时返回 null\n"
            "4. 日期/时间使用 ISO 8601 格式\n"
            "5. 布尔值使用 true/false\n"
            "6. 数值保持数值类型\n"
            "7. 以 TOON 的表格数组格式输出，表头固定为 values[N]{field,type,value}:，N 为行数\n"
            "8. 使用 2 空格缩进；不要添加任何额外文字，仅返回 TOON 内容\n"
        )
    
    def _build_prompt(
        self,
        content: str,
        schema: List[SchemaField],
        image: Optional[bytes] = None,
    ) -> str:
        """构建优化的 Prompt（TOON 输出示例）"""
        schema_rows = [
            {"name": f.name, "field": f.field, "type": f.type, "required": f.required}
            for f in schema
        ]
        schema_toon = schema_to_toon(schema_rows)

        # 构建 TOON 输出格式示例
        rows = []
        for field in schema:
            example = self._get_example_value(field.type)
            example_str = "true" if example is True else ("false" if example is False else str(example))
            rows.append(f"  {field.field},{field.type},{example_str}")
        toon_example = f"values[{len(schema)}]{{field,type,value}}:\n" + "\n".join(rows)

        prompt = f"""请从以下文本或图像内容中提取信息，并按照指定的 schema 返回 TOON 数据。

【Schema定义（TOON）】
```toon
{schema_toon}
```

【待提取的文本内容】
{content}

【输出格式要求（TOON）】
请严格输出如下 TOON 表结构：
```toon
{toon_example}
```

【特别说明】
- 仅提取schema中定义的字段
- 严格按照指定的字段类型进行类型转换
- 如果字段为必填但内容中找不到相关信息，设置为null
- 日期字段使用ISO 8601格式
- 布尔值使用true/false
- 数值保持数值类型
 
请仅返回 TOON 内容，不要添加其他说明文字。"""

        return prompt
    
    def _get_example_value(self, field_type: str):
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
        """解析 LLM 响应（TOON）"""
        try:
            toon_text = extract_toon_block(response or "")
            parsed = toon_decode(toon_text)
            rows = extract_values_list(parsed)

            schema_dict = {field.field: field for field in schema}

            extracted_values: List[ExtractedValue] = []
            for item in rows:
                field_name = item.get("field")
                field_type = item.get("type")
                value = item.get("value")

                if not isinstance(field_name, str):
                    continue
                if field_name not in schema_dict:
                    logger.warning(f"字段 {field_name} 不在schema中，跳过")
                    continue

                field_type_str = str(field_type) if field_type is not None else "text"
                converted_value = self._convert_value(value, field_type_str)

                extracted_values.append(
                    ExtractedValue(
                        field=field_name,
                        type=field_type_str,
                        value=converted_value,
                    )
                )
            
            logger.info(f"成功解析{len(extracted_values)}个字段 (TOON)")
            return extracted_values
            
        except Exception as e:
            logger.error(f"TOON 解析失败: {str(e)}")
            raise LLMException(f"无法解析LLM的 TOON 响应: {str(e)}")
