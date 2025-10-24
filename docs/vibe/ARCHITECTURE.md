# 架构设计文档

## 系统概览

LLM Document Parser 是一个基于 FastAPI 的数据提取系统，用于从多种来源的文件或文本中，根据指定的 schema，使用大语言模型进行智能数据提取。

## 架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                         HTTP Client                              │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FastAPI Router Layer                          │
│                    (app/api/routes.py)                           │
│                                                                   │
│  POST /api/v1/extract ──► 验证请求 ──► 调用服务层              │
└────────────────────────┬────────────────────────────────────────┘
                         │
        ┌────────────────┴────────────────┐
        ▼                                  ▼
┌──────────────────────┐         ┌──────────────────────┐
│  Service Layer       │         │   Exception Handler  │
│  (extract_service)   │         │   (core/exceptions)  │
│                      │         └──────────────────────┘
│ ┌──────────────────┐ │
│ │ 1.获取文件内容  │ │
│ │ 2.提取文本      │ │
│ │ 3.使用LLM处理  │ │
│ └──────────────────┘ │
└────────┬─────────────┘
         │
     ┌───┴─────────────────────────┬──────────────┐
     │                             │              │
     ▼                             ▼              ▼
┌──────────────┐        ┌──────────────────┐  ┌─────────────┐
│MinIO Service │        │File Service      │  │ LLM Layer   │
│              │        │(Unstructured)    │  │ (工厂模式)  │
│• 文件下载    │        │                  │  │             │
│• URL解析     │        │• PDF处理         │  │ ┌─────────┐ │
│• S3操作      │        │• DOCX处理        │  │ │OpenAI   │ │
│              │        │• TXT处理         │  │ │LLM      │ │
│              │        │• 文本提取        │  │ │         │ │
│              │        │                  │  │ │• Extract│ │
│              │        │                  │  │ │• Prompt │ │
│              │        │                  │  │ │• Parse  │ │
└──────────────┘        └──────────────────┘  │ │         │ │
                                              │ └─────────┘ │
                                              │             │
                                              │ 扩展点:     │
                                              │ • Azure    │
                                              │ • Claude   │
                                              │ • etc.     │
                                              └─────────────┘
```

## 分层架构详解

### 1. API 层 (app/api/)

**职责**: 处理 HTTP 请求和响应

**核心文件**:
- `routes.py`: 定义 API 端点

**主要特点**:
- 请求验证（Pydantic models）
- 异常捕获和转换
- 响应序列化
- OpenAPI 文档生成

```python
@router.post("/api/v1/extract")
async def extract(request: ExtractRequest) -> ExtractResponse:
    # 1. 验证请求
    # 2. 调用服务
    # 3. 返回响应
    pass
```

### 2. 服务层 (app/services/)

**职责**: 协调各个组件完成业务逻辑

**核心文件**:
- `extract_service.py`: 主服务，协调流程
- `minio_service.py`: 文件下载服务
- `file_service.py`: 文件处理服务

**流程**:
```
1. 获取文件内容 (MinIO或原始文本)
2. 提取文本 (使用Unstructured)
3. 调用LLM进行数据提取
4. 返回结果
```

### 3. LLM 层 (app/llm/)

**职责**: 封装 LLM 调用逻辑

**核心文件**:
- `base.py`: 抽象基类
- `openai_llm.py`: OpenAI 实现
- `factory.py`: 工厂模式

**工厂模式设计**:

```python
class BaseLLM(ABC):
    @abstractmethod
    async def extract(...) -> List[ExtractedValue]:
        pass
    
    @abstractmethod
    def _build_prompt(...) -> str:
        pass
    
    @abstractmethod
    def _parse_response(...) -> List[ExtractedValue]:
        pass

class LLMFactory:
    _providers = {"openai": OpenAILLM}
    
    @classmethod
    def create(provider: str) -> BaseLLM:
        return _providers[provider]()
    
    @classmethod
    def register(provider: str, llm_class: Type[BaseLLM]):
        _providers[provider] = llm_class
```

**优势**:
- 易于添加新的LLM提供商
- 运行时选择不同的LLM
- 依赖注入，便于测试
- 遵循开闭原则

### 4. 核心层 (app/core/)

**职责**: 应用配置和异常定义

**核心文件**:
- `config.py`: 使用 Pydantic Settings 管理配置
- `exceptions.py`: 自定义异常类

**配置管理**:
```python
class Settings(BaseSettings):
    OPENAI_API_KEY: str
    MINIO_ENDPOINT: str
    # ... 更多配置
    
    class Config:
        env_file = ".env"
```

**异常体系**:
```
AppException
├── MinIOException
├── FileProcessingException
├── LLMException
└── ValidationException
```

### 5. 数据模型层 (app/models/)

**职责**: 定义所有数据模型

**核心文件**:
- `schemas.py`: Pydantic models

**主要模型**:
- `SchemaField`: Schema 字段定义
- `ExtractRequest`: 请求模型
- `ExtractedValue`: 提取结果
- `ExtractResponse`: 响应模型

## 数据流

### 端到端数据流

```
用户请求
  ↓
API路由验证
  ↓
Service: 获取文件内容
  ├─ 如果source=minio → MinIOService.download_file()
  └─ 如果source=raw → 直接使用
  ↓
Service: 提取文本
  ├─ 如果source=minio → FileService.extract_text_from_file()
  └─ 如果source=raw → FileService.extract_text_from_raw()
  ↓
Service: 使用LLM提取
  ├─ LLMFactory.create("openai")
  ├─ LLM.extract()
  │   ├─ 构建Prompt
  │   ├─ 调用OpenAI API
  │   └─ 解析Response
  └─ 返回结果
  ↓
API路由返回响应
  ↓
用户收到结果
```

### Prompt 构建策略

```python
Prompt = SystemPrompt + UserPrompt

UserPrompt = """
【Schema定义】
{
  "fields": [
    {"name": "...", "field": "...", "type": "..."},
    ...
  ]
}

【输出格式示例】
[
  {"field": "...", "type": "...", "value": "..."},
  ...
]

【待提取文本】
{content}

【特别说明】
- 遵循type约束
- 必填字段若无法提取则设为null
- 确保JSON格式有效
"""
```

**优化点**:
1. **清晰的任务定义**: 明确告诉LLM做什么
2. **Schema明确**: 使用JSON格式描述期望的输出
3. **示例驱动**: 通过示例示范输出格式（Few-shot）
4. **类型约束**: 明确每个字段的类型要求
5. **容错机制**: 说明如何处理边界情况

## 扩展性设计

### 1. 添加新的 LLM 提供商

继承 `BaseLLM`:

```python
class ClaudeLLM(BaseLLM):
    async def extract(self, content, schema, model):
        # 实现Claude特定的逻辑
        pass
    
    def _build_prompt(self, content, schema):
        # 构建Claude特定的prompt
        pass
    
    def _parse_response(self, response, schema):
        # 解析Claude特定的响应
        pass

# 注册到工厂
LLMFactory.register("claude", ClaudeLLM)
```

### 2. 添加新的文件处理器

扩展 `FileProcessingService`:

```python
class FileProcessingService:
    @staticmethod
    async def extract_text_from_custom_format(
        file_content: bytes,
    ) -> str:
        # 实现自定义格式的处理
        pass
```

### 3. 添加新的存储后端

创建新的服务类:

```python
class S3Service:
    async def download_file(self, url: str) -> bytes:
        # AWS S3实现
        pass

class OSSService:
    async def download_file(self, url: str) -> bytes:
        # 阿里云OSS实现
        pass
```

## 错误处理机制

### 异常处理流程

```
LLM调用 ──错误→ 捕获异常
  ↓
转换为AppException子类
  ↓
APIRouter捕获
  ↓
转换为HTTPException
  ↓
返回给客户端
```

### 异常恢复策略

1. **重试机制**: 对于临时性错误进行重试
2. **降级处理**: 备选方案
3. **超时控制**: 防止无限等待
4. **日志记录**: 完整的错误信息

## 性能考虑

### 1. 异步处理

所有I/O操作都使用异步:
- FastAPI 异步路由
- AsyncOpenAI 客户端
- MinIO 异步调用（可扩展）

### 2. 连接池

```python
# OpenAI客户端自动管理连接池
client = AsyncOpenAI(api_key=key)

# MinIO 可以考虑连接池
minio_client = Minio(...)
```

### 3. 缓存

```python
# 考虑添加缓存中间件
from fastapi_cache2 import FastAPICache2

@cached(expire=3600)
async def extract(...):
    pass
```

### 4. 监控和日志

```python
# 结构化日志
logger.info(
    "Extract completed",
    extra={
        "source": "minio",
        "duration": elapsed_time,
        "fields_count": len(results),
    }
)
```

## 安全考虑

### 1. API 密钥管理

```python
# 环境变量
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 不记录敏感信息
logger.info(f"Using API key: {key[:10]}...")
```

### 2. 输入验证

```python
# Pydantic 自动验证
class ExtractRequest(BaseModel):
    source: Literal["minio", "raw"]  # 严格类型
    file: str = Field(..., max_length=100000)  # 长度限制
    schema: List[SchemaField]  # 结构验证
```

### 3. 请求限制

```python
# 添加速率限制
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/extract")
@limiter.limit("100/minute")
async def extract(request: ExtractRequest):
    pass
```

## 部署架构

### 开发环境

```
单进程 Uvicorn
└─ app.main:app
```

### 生产环境

```
负载均衡器 (Nginx/HAProxy)
  │
  ├─ Gunicorn Worker 1
  │  └─ Uvicorn
  ├─ Gunicorn Worker 2
  │  └─ Uvicorn
  └─ Gunicorn Worker N
     └─ Uvicorn

Redis 缓存 (可选)
MinIO 集群
OpenAI API
```

## 配置管理

### 环境分离

```
.env.development  # 开发配置
.env.production   # 生产配置
.env.test         # 测试配置
```

### 配置优先级

```
环境变量 > .env文件 > 默认值
```

## 监控和可观测性

### 日志

```python
# 使用结构化日志
logger.info("Event", extra={"key": "value"})

# 日志级别
DEBUG   # 详细调试信息
INFO    # 正常业务流程
WARNING # 潜在问题
ERROR   # 错误，需要处理
```

### 指标收集

```python
# 考虑集成Prometheus
from prometheus_client import Counter, Histogram

request_count = Counter("requests_total", "Total requests")
request_duration = Histogram("request_duration_seconds", "Request duration")
```

### 健康检查

```python
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

## 版本管理

### API 版本

```
/api/v1/extract  # 当前版本
/api/v2/extract  # 未来版本
```

### 向后兼容性

- 新字段都应该是可选的
- 不删除已有字段
- 使用弃用头进行通知

## 总结

该架构的设计特点:

1. **分层清晰**: 各层职责明确
2. **高度解耦**: 使用依赖注入和工厂模式
3. **易于扩展**: 添加新LLM或文件类型只需添加新类
4. **异步优先**: 充分利用Python异步特性
5. **错误处理完善**: 自定义异常体系
6. **可观测性好**: 完整的日志记录
7. **安全可靠**: 输入验证、密钥管理等
