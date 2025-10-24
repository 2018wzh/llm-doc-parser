# Custom LLM 提供商 - OpenAI 兼容 API

## 概述

Custom 提供商允许您使用任何兼容 OpenAI API 的本地或远程 LLM 服务。这包括：

- **LM Studio** - 本地 AI 模型运行器
- **Ollama** - 轻量级 LLM 框架
- **vLLM** - 高效的 LLM 推理服务
- **LocalAI** - 开源的 OpenAI API 替代品
- **其他兼容服务** - 任何实现 OpenAI API 的服务

## 快速开始

### 1. 配置 .env 文件

```bash
LLM_PROVIDER=custom
CUSTOM_BASE_URL=http://localhost:1234/v1
CUSTOM_API_KEY=not-needed
CUSTOM_MODEL=gpt-3.5-turbo
```

### 2. 发送提取请求

```json
POST /api/v1/extract

{
  "source": "raw",
  "file": "张三是一名工程师，出生于1990年5月15日。",
  "provider": "custom",
  "model": "neural-chat",
  "custom_base_url": "http://localhost:1234/v1",
  "custom_api_key": "not-needed",
  "schema": [
    {
      "name": "姓名",
      "field": "name",
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

## 本地服务设置

### LM Studio

LM Studio 是一个用户友好的 GUI 应用程序，用于在 Mac、Windows 或 Linux 上运行 LLM。

#### 安装和启动：

1. 下载 [LM Studio](https://lmstudio.ai/)
2. 启动应用程序
3. 下载一个模型（例如 Neural Chat）
4. 在"Local Server"标签中启动服务器

#### 配置：

```env
LLM_PROVIDER=custom
CUSTOM_BASE_URL=http://localhost:1234/v1
CUSTOM_API_KEY=not-needed
CUSTOM_MODEL=neural-chat
```

#### 使用示例：

```python
request = ExtractRequest(
    source="raw",
    file="你的文本内容",
    provider="custom",
    model="neural-chat",
    custom_base_url="http://localhost:1234/v1",
    schema=[...]
)
```

### Ollama

Ollama 是一个轻量级的命令行工具，可以轻松在 macOS、Linux 和 Windows（WSL 2）上运行。

#### 安装：

```bash
# macOS
brew install ollama

# Linux
curl https://ollama.ai/install.sh | sh

# Windows
# 下载安装程序: https://ollama.ai/download/windows
```

#### 启动服务：

```bash
# 拉取模型
ollama pull llama2
ollama pull mistral
ollama pull neural-chat

# 启动 API 服务（在后台运行）
# Ollama 默认使用 http://localhost:11434
# 启用 OpenAI API 兼容模式（需要最新版本）
OLLAMA_HOST=0.0.0.0:11434 ollama serve
```

#### 配置：

```env
LLM_PROVIDER=custom
CUSTOM_BASE_URL=http://localhost:11434/v1
CUSTOM_API_KEY=not-needed
CUSTOM_MODEL=llama2
```

#### 使用示例：

```python
request = ExtractRequest(
    source="raw",
    file="你的文本内容",
    provider="custom",
    model="llama2",
    custom_base_url="http://localhost:11434/v1",
    schema=[...]
)
```

### vLLM

vLLM 是一个快速而易用的 LLM 推理和服务库。

#### 安装：

```bash
pip install vllm
```

#### 启动服务：

```bash
# 使用 Mistral 模型
python -m vllm.entrypoints.openai.api_server \
    --model mistral-community/Mistral-7B-Instruct-v0.1 \
    --port 8000

# 或使用 Llama 2
python -m vllm.entrypoints.openai.api_server \
    --model meta-llama/Llama-2-7b-hf \
    --port 8000
```

#### 配置：

```env
LLM_PROVIDER=custom
CUSTOM_BASE_URL=http://localhost:8000/v1
CUSTOM_API_KEY=not-needed
CUSTOM_MODEL=mistral-community/Mistral-7B-Instruct-v0.1
```

#### 使用示例：

```python
request = ExtractRequest(
    source="raw",
    file="你的文本内容",
    provider="custom",
    model="mistral-community/Mistral-7B-Instruct-v0.1",
    custom_base_url="http://localhost:8000/v1",
    schema=[...]
)
```

### LocalAI

LocalAI 是一个开源的、无依赖的 OpenAI API 替代品。

#### 使用 Docker 启动：

```bash
# 最简单的方式
docker run -p 8080:8080 localai/localai:latest-aio-cpu

# 或者使用 GPU
docker run --gpus all -p 8080:8080 localai/localai:latest-aio-gpu-nvidia
```

#### 本地安装：

```bash
# 下载二进制文件
wget https://github.com/go-skynet/LocalAI/releases/download/v1.x.x/local-ai-Linux-x86_64

# 使模块可执行
chmod +x local-ai-Linux-x86_64

# 运行
./local-ai-Linux-x86_64 api
```

#### 配置：

```env
LLM_PROVIDER=custom
CUSTOM_BASE_URL=http://localhost:8080/v1
CUSTOM_API_KEY=not-needed
CUSTOM_MODEL=gpt-4-turbo
```

#### 使用示例：

```python
request = ExtractRequest(
    source="raw",
    file="你的文本内容",
    provider="custom",
    model="gpt-4-turbo",
    custom_base_url="http://localhost:8080/v1",
    schema=[...]
)
```

## API 参数说明

### 请求参数

| 参数名 | 类型 | 必需 | 说明 |
|--------|------|------|------|
| provider | string | 是 | 固定为 "custom" |
| custom_base_url | string | 是 | LLM 服务的 API 基础 URL |
| custom_api_key | string | 否 | API 密钥，某些本地服务不需要 |
| model | string | 否 | 模型名称，不提供时使用默认值 |
| file | string | 是 | 文本内容或 MinIO URL |
| schema | array | 是 | 提取的字段定义 |

### 常见的 base_url

| 服务 | 默认 URL |
|------|---------|
| LM Studio | http://localhost:1234/v1 |
| Ollama | http://localhost:11434/v1 |
| vLLM | http://localhost:8000/v1 |
| LocalAI | http://localhost:8080/v1 |
| text-generation-webui | http://localhost:5000/v1 |

## 生产使用建议

### 1. 使用环境变量

在生产环境中，始终使用环境变量设置敏感信息：

```env
LLM_PROVIDER=custom
CUSTOM_BASE_URL=https://your-server.com/v1
CUSTOM_API_KEY=your-secret-key
CUSTOM_MODEL=your-model-name
```

### 2. 错误处理

```python
try:
    result = await extract_service.extract(request)
except LLMException as e:
    logger.error(f"LLM 提取失败: {str(e)}")
    # 处理错误
```

### 3. 性能优化

- **使用更小的模型** 以获得更快的响应时间
- **启用量化** 以减少内存使用
- **使用批处理** 以提高吞吐量

### 4. 监控和日志

```python
import logging

logger = logging.getLogger(__name__)
logger.info(f"使用 {provider} 提供商提取数据")
logger.debug(f"API 基础 URL: {custom_base_url}")
```

## 故障排除

### 连接拒绝错误

```
Error: OpenAI 兼容 API 调用失败: Connection refused
```

**解决方案**：
1. 检查服务是否正在运行
2. 验证 base_url 是否正确
3. 检查防火墙设置

### 模型不找到错误

```
Error: Model not found
```

**解决方案**：
1. 确保模型已下载/安装
2. 验证模型名称是否正确
3. 查看服务日志获取更多信息

### 超时错误

```
Error: Request timeout
```

**解决方案**：
1. 增加 timeout 值
2. 使用更小的模型
3. 检查网络连接

### 内存不足错误

```
Error: Out of memory
```

**解决方案**：
1. 使用更小的模型
2. 启用量化
3. 增加系统内存或使用 GPU

## 完整示例

```python
import asyncio
from app.models import ExtractRequest, SchemaField
from app.services import ExtractService


async def main():
    service = ExtractService()
    
    request = ExtractRequest(
        source="raw",
        file="""
        我是张三，今年 28 岁，工作 5 年。
        目前在阿里巴巴担任高级工程师，年薪 60 万。
        """,
        provider="custom",
        model="neural-chat",
        custom_base_url="http://localhost:1234/v1",
        schema=[
            SchemaField(
                name="姓名",
                field="name",
                type="text",
                required=True
            ),
            SchemaField(
                name="年龄",
                field="age",
                type="int",
                required=True
            ),
            SchemaField(
                name="工作年限",
                field="experience",
                type="int",
                required=True
            ),
            SchemaField(
                name="公司",
                field="company",
                type="text",
                required=True
            ),
            SchemaField(
                name="年薪",
                field="salary",
                type="int",
                required=True
            ),
        ]
    )
    
    result = await service.extract(request)
    
    for item in result:
        print(f"{item.field}: {item.value}")


if __name__ == "__main__":
    asyncio.run(main())
```

## 许可证

支持的本地 LLM 框架使用不同的许可证：

- **LM Studio** - 专有许可证
- **Ollama** - MIT 许可证
- **vLLM** - Apache 2.0 许可证
- **LocalAI** - MIT 许可证

在生产使用前，请检查相应项目的许可证。
