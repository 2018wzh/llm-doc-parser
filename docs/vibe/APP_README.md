# LLM Document Parser

一个优化的 FastAPI 应用程序，用于从 MinIO 下载文件（或处理原始文本），使用 Unstructured 库提取文本，然后通过 LLM 将内容转换为指定 schema 的 JSON。

## ✨ 核心特性

- **多源支持**: 支持从 MinIO 和原始文本两种来源获取数据
- **灵活的文件处理**: 使用 Unstructured 库支持多种文件格式（PDF、DOCX、TXT 等）
- **LLM 工厂模式**: 易于扩展的工厂模式实现，目前支持 OpenAI API
- **优化的 Prompt**: 采用 Few-shot 学习和清晰的指令设计
- **类型转换**: 自动进行类型转换和验证（text、int、float、boolean、date、datetime）
- **异常处理**: 完善的异常处理和日志记录
- **CORS 支持**: 开箱即用的跨域资源共享
- **API 文档**: 自动生成的 OpenAPI/Swagger 文档

## 📋 项目结构

```
llm-doc-parser/
├── app/
│   ├── api/                    # API路由层
│   │   ├── routes.py          # API端点定义
│   │   └── __init__.py
│   ├── core/                   # 核心配置和异常
│   │   ├── config.py          # 应用配置
│   │   ├── exceptions.py      # 自定义异常
│   │   └── __init__.py
│   ├── models/                 # 数据模型
│   │   ├── schemas.py         # Pydantic models
│   │   └── __init__.py
│   ├── llm/                    # LLM实现
│   │   ├── base.py            # 基础接口
│   │   ├── openai_llm.py      # OpenAI实现
│   │   ├── factory.py         # 工厂模式
│   │   └── __init__.py
│   ├── services/               # 业务逻辑层
│   │   ├── minio_service.py   # MinIO服务
│   │   ├── file_service.py    # 文件处理服务
│   │   ├── extract_service.py # 提取服务
│   │   └── __init__.py
│   ├── main.py                # FastAPI应用
│   └── __init__.py
├── tests/                      # 测试文件
│   ├── test_api.py            # API测试
│   └── __init__.py
├── .env.example               # 环境配置示例
├── run.py                     # 启动脚本
├── requirements.txt           # 依赖管理
└── README.md                  # 本文件
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并填入你的配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
# OpenAI配置
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_BASE_URL=  # 可选，用于自定义OpenAI基础URL

# MinIO配置（如果使用MinIO源）
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_SECURE=false

# 应用配置
APP_TITLE=LLM Document Parser
APP_VERSION=1.0.0
DEBUG=false
```

### 3. 运行应用

```bash
# 方式1: 使用Python脚本
python run.py

# 方式2: 使用uvicorn
uvicorn app.main:app --reload

# 方式3: 使用PowerShell (Windows)
python run.py
```

应用将在 `http://localhost:8000` 启动

### 4. 查看 API 文档

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📚 API 文档

### POST /api/v1/extract

从文件或文本内容根据指定 schema 提取数据。

#### 请求参数

```json
{
    "source": "raw",           // 文件来源: "minio" 或 "raw"
    "file": "文本内容",         // MinIO URL 或原始文本
    "schema": [                // 数据Schema定义
        {
            "name": "人名",     // 字段详情描述
            "field": "name",   // 字段名称
            "type": "text",    // 字段类型: text|int|float|boolean|date|datetime
            "required": true   // 是否必填
        }
    ],
    "model": "gpt-4-turbo-preview"  // LLM模型（可选，默认gpt-4-turbo-preview）
}
```

#### 字段类型说明

| 类型 | 说明 | 示例 |
|------|------|------|
| text | 文本类型 | "张三" |
| int | 整数类型 | 25 |
| float | 浮点数类型 | 3.14 |
| boolean | 布尔类型 | true/false |
| date | 日期类型 | "2024-01-01" |
| datetime | 日期时间 | "2024-01-01 12:00:00" |

#### 成功响应 (200)

```json
{
    "data": [
        {
            "field": "name",
            "type": "text",
            "value": "张三"
        },
        {
            "field": "age",
            "type": "int",
            "value": 30
        },
        {
            "field": "birth_date",
            "type": "date",
            "value": "1994-05-15"
        }
    ],
    "code": "200",
    "message": "Success"
}
```

#### 错误响应 (422/500)

```json
{
    "code": "VALIDATION_ERROR",
    "message": "错误描述"
}
```

### 使用示例

#### 示例 1: 从原始文本提取信息

```bash
curl -X POST "http://localhost:8000/api/v1/extract" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "raw",
    "file": "张三是一名30岁的软件工程师，出生于1994年5月15日",
    "schema": [
        {
            "name": "人名",
            "field": "name",
            "type": "text",
            "required": true
        },
        {
            "name": "年龄",
            "field": "age",
            "type": "int",
            "required": true
        },
        {
            "name": "职业",
            "field": "occupation",
            "type": "text",
            "required": false
        },
        {
            "name": "出生日期",
            "field": "birth_date",
            "type": "date",
            "required": false
        }
    ]
}'
```

#### 示例 2: 从 MinIO 下载 PDF 并提取

```bash
curl -X POST "http://localhost:8000/api/v1/extract" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "minio",
    "file": "http://localhost:9000/documents/resume.pdf",
    "schema": [
        {
            "name": "姓名",
            "field": "name",
            "type": "text",
            "required": true
        },
        {
            "name": "电话",
            "field": "phone",
            "type": "text",
            "required": true
        },
        {
            "name": "邮箱",
            "field": "email",
            "type": "text",
            "required": true
        }
    ],
    "model": "gpt-4-turbo-preview"
}'
```

## 🏗️ 架构设计

### 分层架构

- **API Layer**: FastAPI 路由，处理 HTTP 请求和响应
- **Service Layer**: 业务逻辑，协调各个服务
- **LLM Layer**: LLM 实现，使用工厂模式
- **Utility Layer**: MinIO、文件处理等工具服务

### 工厂模式

LLM 模块使用工厂模式，便于扩展新的 LLM 提供商：

```python
# 使用工厂创建LLM实例
llm = LLMFactory.create("openai")

# 扩展：注册新的提供商
LLMFactory.register("azure", AzureOpenAILLM)
```

### Prompt 优化

采用了以下优化策略：

1. **清晰的任务描述**: 明确告诉LLM要做什么
2. **Schema 定义**: 提供详细的字段信息
3. **输出格式示例**: 使用 Few-shot learning
4. **类型约束**: 明确每个字段的类型要求
5. **边界情况处理**: 说明如何处理缺失字段

```python
prompt = """
【Schema定义】
[字段定义JSON]

【待提取的文本内容】
[实际文本]

【输出格式要求】
[输出示例]

【特别说明】
[特殊处理说明]
"""
```

## 🔧 配置说明

### app/core/config.py

应用全局配置，支持从 `.env` 文件读取：

```python
class Settings(BaseSettings):
    OPENAI_API_KEY: str                    # OpenAI API密钥（必需）
    OPENAI_BASE_URL: Optional[str] = None # OpenAI基础URL（可选）
    MINIO_ENDPOINT: str                   # MinIO端点
    MINIO_ACCESS_KEY: str                 # MinIO访问密钥
    MINIO_SECRET_KEY: str                 # MinIO秘钥
    MINIO_SECURE: bool = False            # 是否使用HTTPS
    MAX_FILE_SIZE: int                    # 最大文件大小
    ALLOWED_FILE_TYPES: list              # 允许的文件类型
```

## 🎯 扩展性设计

### 添加新的 LLM 提供商

1. 创建新类继承 `BaseLLM`:

```python
from app.llm.base import BaseLLM

class AzureOpenAILLM(BaseLLM):
    async def extract(self, content, schema, model):
        # 实现提取逻辑
        pass
    
    def _build_prompt(self, content, schema):
        # 实现prompt构建
        pass
    
    def _parse_response(self, response, schema):
        # 实现响应解析
        pass
```

2. 注册到工厂:

```python
from app.llm import LLMFactory
from your_module import AzureOpenAILLM

LLMFactory.register("azure", AzureOpenAILLM)
```

### 添加新的文件类型支持

Unstructured 库已支持多种文件格式，添加新类型只需更新配置或文件处理逻辑。

## 📝 日志

应用使用 Python 的标准 `logging` 模块，日志格式：

```
2024-01-15 10:30:45,123 - app.services.extract_service - INFO - 开始数据提取
```

日志级别：
- `INFO`: 正常业务流程日志
- `WARNING`: 可处理的错误
- `ERROR`: 严重错误，需要处理

## ✅ 测试

运行测试用例：

```bash
# 运行所有测试
pytest tests/

# 运行特定测试
pytest tests/test_api.py::test_health_check -v

# 生成覆盖率报告
pytest tests/ --cov=app --cov-report=html
```

## 🐛 异常处理

应用定义了多种自定义异常，便于错误处理：

- `AppException`: 基础异常
- `MinIOException`: MinIO 相关错误
- `FileProcessingException`: 文件处理错误
- `LLMException`: LLM 相关错误
- `ValidationException`: 验证错误

所有异常都会被转换为 HTTP 响应并返回给客户端。

## 🔐 安全性建议

1. **环境变量**: 不要在代码中硬编码 API 密钥
2. **HTTPS**: 生产环境使用 HTTPS
3. **速率限制**: 考虑添加 API 速率限制中间件
4. **输入验证**: 已内置 Pydantic 验证
5. **日志脱敏**: 不记录敏感信息（如完整的 API 密钥）

## 📦 依赖管理

主要依赖版本：
- FastAPI >= 0.104.1
- OpenAI >= 1.3.0
- Unstructured >= 0.10.30
- Minio >= 7.2.0
- Pydantic >= 2.5.0

## 🌐 健康检查

```bash
curl http://localhost:8000/health
```

响应：
```json
{
    "status": "healthy",
    "service": "LLM Document Parser",
    "version": "1.0.0"
}
```

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📞 支持

如有问题，请查看：
1. API 文档: http://localhost:8000/docs
2. 日志输出
3. GitHub Issues
