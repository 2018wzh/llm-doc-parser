"""
OpenAI 兼容的 Custom LLM 实现

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
            
            response_text = response.choices[0].message.content
            
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
        """构建优化的 Prompt"""
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
        
        prompt = f"""请从以下文本或图像内容中提取信息，并按照指定的schema返回JSON数据。

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
        """解析 LLM 响应"""
        try:
            # 处理可能的 markdown 代码块
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
            
            response_data = json.loads(response)
            
            if not isinstance(response_data, list):
                response_data = [response_data]
            
            schema_dict = {field.field: field for field in schema}
            
            extracted_values = []
            for item in response_data:
                if not isinstance(item, dict):
                    continue
                
                field_name = item.get("field")
                field_type = item.get("type")
                value = item.get("value")
                
                if field_name not in schema_dict:
                    logger.warning(f"字段 {field_name} 不在schema中，跳过")
                    continue
                
                converted_value = self._convert_value(value, field_type)
                
                extracted_values.append(
                    ExtractedValue(
                        field=field_name,
                        type=field_type,
                        value=converted_value,
                    )
                )
            
            logger.info(f"成功解析{len(extracted_values)}个字段")
            return extracted_values
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {str(e)}")
            raise LLMException(f"无法解析LLM响应: {str(e)}")
