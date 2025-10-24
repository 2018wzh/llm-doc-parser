# 多 LLM 提供商使用指南

本应用支持多个 LLM 提供商，包括 OpenAI、Azure OpenAI、Anthropic Claude 和 Google Gemini。本指南将详细说明如何配置和使用每个提供商。

## 支持的提供商

| 提供商 | 模型 | 特点 | 配置难度 |
|--------|------|------|--------|
| **OpenAI** | GPT-4o, GPT-4o-mini | 功能强大，API 最稳定 | 简单 |
| **Azure OpenAI** | 与 OpenAI 相同 | 企业级，低延迟，数据驻留 | 中等 |
| **Anthropic Claude** | Claude 3 系列 | 长上下文，优秀的推理能力 | 简单 |
| **Google Gemini** | Gemini 2.0/1.5 系列 | 多模态，成本低 | 简单 |

## 环境变量配置

### 1. OpenAI（默认）

```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxx
OPENAI_BASE_URL=https://api.openai.com/v1  # 可选，默认为官方地址
OPENAI_MODEL=gpt-4o-mini
```

**获取 API Key**：
- 访问 [OpenAI 官网](https://platform.openai.com/api-keys)
- 创建新的 API Key
- 复制并保存到 `.env` 文件

### 2. Azure OpenAI

```bash
LLM_PROVIDER=azure
AZURE_OPENAI_KEY=xxxxxxxxxxxxxxxxxxxxxxxx
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_DEPLOYMENT=your-deployment-name
```

**配置步骤**：
1. 在 Azure 门户创建 OpenAI 资源
2. 获取 API Key（在"密钥和端点"部分）
3. 获取 Endpoint URL
4. 在 Azure OpenAI Studio 创建部署
5. 记录部署名称

**可用模型**：
- gpt-4-deployment
- gpt-4o-deployment
- gpt-4-turbo-deployment

### 3. Anthropic Claude

```bash
LLM_PROVIDER=claude
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxx
CLAUDE_MODEL=claude-3-sonnet-20240229
```

**获取 API Key**：
- 访问 [Anthropic 控制台](https://console.anthropic.com/)
- 创建新的 API Key
- 复制并保存到 `.env` 文件

**可用模型**：
- `claude-3-opus-20240229` - 最强大的模型，推荐用于复杂任务
- `claude-3-sonnet-20240229` - 平衡的模型，**推荐**
- `claude-3-haiku-20240307` - 最快最便宜的模型

### 4. Google Gemini

```bash
LLM_PROVIDER=gemini
GOOGLE_API_KEY=AIzaSy_xxxxxxxxxxxxxxxxxxxxxxxx
GEMINI_MODEL=gemini-2.0-flash
```

**获取 API Key**：
- 访问 [Google AI Studio](https://aistudio.google.com/app/apikey)
- 点击"创建新的 API Key"
- 创建新项目或选择现有项目
- 复制并保存到 `.env` 文件

**可用模型**：
- `gemini-2.0-flash` - 最新最快的模型
- `gemini-1.5-pro` - 高性能模型
- `gemini-1.5-flash` - 轻量级模型

## 安装依赖

所有 LLM 提供商的依赖已在 `requirements.txt` 中：

```bash
pip install -r requirements.txt
```

如果只想安装特定提供商的依赖：

```bash
# 仅 OpenAI（已内置）
pip install openai==1.3.0

# Azure OpenAI
pip install azure-identity>=1.14.0 azure-openai>=1.10.0

# Anthropic Claude
pip install anthropic>=0.20.0

# Google Gemini
pip install google-generativeai>=0.3.0
```

## API 使用示例

### 基础用法 - 使用默认 OpenAI

```python
import aiohttp
import asyncio

async def extract_with_openai():
    async with aiohttp.ClientSession() as session:
        payload = {
            "source": "raw",
            "file": "张三是一名软件工程师，来自北京",
            "schema": [
                {
                    "name": "人名",
                    "field": "name",
                    "type": "text",
                    "required": True
                },
                {
                    "name": "职位",
                    "field": "position",
                    "type": "text",
                    "required": True
                },
                {
                    "name": "城市",
                    "field": "city",
                    "type": "text",
                    "required": True
                }
            ]
        }
        
        async with session.post(
            "http://localhost:8000/api/v1/extract",
            json=payload
        ) as response:
            return await response.json()

asyncio.run(extract_with_openai())
```

### 使用 Azure OpenAI

```python
payload = {
    "source": "raw",
    "file": "张三是一名软件工程师，来自北京",
    "provider": "azure",  # 指定提供商
    "model": "gpt-4-deployment",  # Azure 部署名称
    "schema": [...]
}
```

### 使用 Claude

```python
payload = {
    "source": "raw",
    "file": "张三是一名软件工程师，来自北京",
    "provider": "claude",
    "model": "claude-3-sonnet-20240229",
    "schema": [...]
}
```

### 使用 Gemini

```python
payload = {
    "source": "raw",
    "file": "张三是一名软件工程师，来自北京",
    "provider": "gemini",
    "model": "gemini-2.0-flash",
    "schema": [...]
}
```

## 性能对比

| 提供商 | 速度 | 成本 | 准确性 | 推荐场景 |
|--------|------|------|--------|---------|
| OpenAI | 快 | 中 | 很高 | 通用、生产环境 |
| Azure | 快 | 中 | 很高 | 企业级、合规要求 |
| Claude | 快 | 低 | 很高 | 长文本、推理任务 |
| Gemini | 很快 | 很低 | 高 | 成本敏感、多模态 |

## 成本估算

### OpenAI GPT-4o-mini
- 输入：$0.00015 / 1K tokens
- 输出：$0.0006 / 1K tokens

### Azure OpenAI（与 OpenAI 相同）
- 需要额外支付计算资源费用

### Claude 3 Sonnet
- 输入：$0.003 / 1M tokens
- 输出：$0.015 / 1M tokens

### Gemini 2.0 Flash
- 输入：$0.075 / 1M tokens
- 输出：$0.3 / 1M tokens

## 故障排查

### 连接失败

检查 API Key 是否正确：

```bash
# 测试 OpenAI
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
  https://api.openai.com/v1/models

# 测试 Anthropic
curl -H "x-api-key: $ANTHROPIC_API_KEY" \
  https://api.anthropic.com/v1/models

# 测试 Google Gemini
curl "https://generativelanguage.googleapis.com/v1/models?key=$GOOGLE_API_KEY"
```

### 超时错误

某些提供商可能响应较慢，可以增加超时时间：

```python
async with session.post(
    "http://localhost:8000/api/v1/extract",
    json=payload,
    timeout=aiohttp.ClientTimeout(total=60)  # 增加超时
) as response:
    ...
```

### JSON 解析错误

某些 LLM 可能返回带有 Markdown 代码块的响应。应用已自动处理此情况。

如果仍然遇到问题，可以启用调试日志：

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 切换提供商

### 方法 1：修改 .env 文件

```bash
# 编辑 .env 文件
LLM_PROVIDER=claude
```

然后重启应用。

### 方法 2：运行时通过 API 切换

```python
payload = {
    "provider": "gemini",  # 在请求中指定
    ...
}
```

## 最佳实践

1. **优先使用 OpenAI**：功能最完整，生态最成熟
2. **成本优化**：使用 Gemini 或 Claude 的轻量级模型
3. **长文本处理**：使用 Claude，支持 200K tokens 上下文
4. **企业环境**：使用 Azure OpenAI，数据驻留本地
5. **多模态**：使用 Gemini，支持图像输入

## 更新提供商

要添加新的 LLM 提供商：

1. 创建新文件 `app/llm/{provider}_llm.py`
2. 继承 `BaseLLM` 类
3. 实现必要方法
4. 在 `app/llm/factory.py` 中注册

示例：

```python
# app/llm/ollama_llm.py
from app.llm.base import BaseLLM

class OllamaLLM(BaseLLM):
    @property
    def provider_name(self) -> str:
        return "ollama"
    
    async def extract(self, content, schema, model):
        # 实现提取逻辑
        pass
    
    def get_available_models(self):
        # 返回可用模型列表
        pass
    
    async def validate_connection(self):
        # 验证连接
        pass
```

然后在 `factory.py` 中注册：

```python
from app.llm.ollama_llm import OllamaLLM

LLMFactory.register("ollama", OllamaLLM)
```

## 参考资源

- [OpenAI API 文档](https://platform.openai.com/docs/)
- [Azure OpenAI 文档](https://learn.microsoft.com/zh-cn/azure/ai-services/openai/)
- [Anthropic API 文档](https://docs.anthropic.com/)
- [Google Gemini API 文档](https://ai.google.dev/docs)

## 支持

如遇到问题，请：

1. 检查 API Key 是否正确
2. 查看日志文件获取详细错误信息
3. 访问提供商的官方文档
4. 提交 Issue 到项目仓库
