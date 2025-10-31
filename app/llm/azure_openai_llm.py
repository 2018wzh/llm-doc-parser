"""
Azure OpenAI LLM 实现
"""
import json
import logging
from typing import List

from openai import AsyncAzureOpenAI

from app.models import SchemaField, ExtractedValue
from app.core import LLMException, settings
from .base import BaseLLM, ModelInfo

logger = logging.getLogger(__name__)


class AzureOpenAILLM(BaseLLM):
    """Azure OpenAI LLM 实现"""
    
    @property
    def provider_name(self) -> str:
        """提供商名称"""
        return "azure"
    
    def __init__(self):
        """初始化 Azure OpenAI 客户端"""
        self.client = AsyncAzureOpenAI(
            api_key=settings.AZURE_OPENAI_KEY,
            api_version=settings.AZURE_OPENAI_API_VERSION,
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
        )
        self.deployment_name = settings.AZURE_OPENAI_DEPLOYMENT
    
    async def extract(
        self,
        content: str,
        schema: List[SchemaField],
        model: str,
    ) -> List[ExtractedValue]:
        """使用 Azure OpenAI 提取数据"""
        try:
            prompt = self._build_prompt(content, schema)
            
            logger.info(f"开始调用 Azure OpenAI，部署: {self.deployment_name}")
            
            response = await self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt},
                ],
                temperature=0,
                response_format={"type": "json_object"},
            )
            
            response_text = response.choices[0].message.content
            logger.info("Azure OpenAI 调用成功")
            
            return self._parse_response(response_text, schema)
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON 解析错误: {str(e)}")
            raise LLMException(f"LLM 响应 JSON 解析失败: {str(e)}")
        except Exception as e:
            logger.error(f"Azure OpenAI 调用失败: {str(e)}")
            raise LLMException(f"Azure OpenAI 调用失败: {str(e)}")
    
    def get_available_models(self) -> List[ModelInfo]:
        """获取可用模型列表"""
        return [
            ModelInfo(
                name=self.deployment_name,
                display_name=f"Azure OpenAI ({self.deployment_name})",
                provider="azure",
                description="Azure OpenAI 部署",
                max_tokens=8192,
                capabilities=["text", "json_mode"],
                cost_per_1k_input=0.03,
                cost_per_1k_output=0.06,
            )
        ]
    
    async def validate_connection(self) -> bool:
        """验证连接"""
        try:
            await self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=1,
            )
            return True
        except Exception as e:
            logger.error(f"Azure OpenAI 连接验证失败: {str(e)}")
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
