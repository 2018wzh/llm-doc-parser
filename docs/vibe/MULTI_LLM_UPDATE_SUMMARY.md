# 多 LLM 提供商支持 - 更新总结

## 概述

项目已成功升级以支持多个 LLM 提供商。现在可以在 OpenAI、Azure OpenAI、Anthropic Claude 和 Google Gemini 之间灵活切换。

## 什么是新增的？

### 1. 新的 LLM 提供商实现

#### Azure OpenAI (`app/llm/azure_openai_llm.py`)
- **描述**：Azure 托管的 OpenAI API
- **优势**：企业级可靠性、数据驻留、专网连接
- **模型**：支持 GPT-4、GPT-4o 等
- **配置**：需要 Azure 部署名称和端点

#### Anthropic Claude (`app/llm/claude_llm.py`)
- **描述**：Anthropic 的 Claude AI 模型
- **优势**：优秀的推理能力、200K token 上下文窗口
- **模型**：Claude 3 系列（Opus、Sonnet、Haiku）
- **特殊功能**：自动 Markdown 代码块解析

#### Google Gemini (`app/llm/gemini_llm.py`)
- **描述**：Google 最新的生成式 AI 模型
- **优势**：最快速度、最低成本、多模态支持
- **模型**：Gemini 2.0 Flash、1.5 Pro、1.5 Flash
- **特点**：支持图像输入、极快的推理速度

### 2. 增强的基础接口 (`app/llm/base.py`)

新增功能：
```python
class ModelCapability(str, Enum):
    """模型能力"""
    TEXT = "text"
    JSON_MODE = "json_mode"
    VISION = "vision"
    FUNCTION_CALLING = "function_calling"
    STREAMING = "streaming"
    LONG_CONTEXT = "long_context"

class ModelInfo(BaseModel):
    """模型信息"""
    name: str                                    # 模型标识
    display_name: str                            # 显示名称
    provider: str                                # 提供商
    capabilities: List[ModelCapability]          # 能力列表
    cost_per_1k_input: Optional[float]           # 输入成本
    cost_per_1k_output: Optional[float]          # 输出成本
```

新增方法：
- `provider_name`: 返回提供商名称
- `get_available_models()`: 获取该提供商的所有可用模型
- `validate_connection()`: 测试与提供商的连接

### 3. 更新的工厂类 (`app/llm/factory.py`)

现在支持 4 个提供商：
- `openai` → OpenAI
- `azure` → Azure OpenAI
- `claude` → Anthropic Claude
- `gemini` → Google Gemini

使用示例：
```python
# 创建 Claude LLM
llm = LLMFactory.create("claude")

# 创建 Gemini LLM
llm = LLMFactory.create("gemini")

# 注册新提供商
LLMFactory.register("ollama", OllamaLLM)
```

### 4. 扩展的配置系统 (`app/core/config.py`)

新增配置项：
```python
LLM_PROVIDER = "openai"                    # 默认提供商

# Azure OpenAI
AZURE_OPENAI_KEY = None
AZURE_OPENAI_ENDPOINT = None
AZURE_OPENAI_API_VERSION = "2024-02-15-preview"
AZURE_OPENAI_DEPLOYMENT = None

# Claude
ANTHROPIC_API_KEY = None
CLAUDE_MODEL = "claude-3-sonnet-20240229"

# Gemini
GOOGLE_API_KEY = None
GEMINI_MODEL = "gemini-2.0-flash"
```

配置验证：自动检查所选提供商的必需环境变量

### 5. 更新的 API 请求模式 (`app/models/schemas.py`)

`ExtractRequest` 现在支持：
```python
provider: Literal["openai", "azure", "claude", "gemini"] = "openai"
model: Optional[str] = None  # 若不指定则使用默认值
```

### 6. 增强的依赖管理 (`requirements.txt`)

新增可选依赖：
```
azure-identity>=1.14.0          # Azure 认证
azure-openai>=1.10.0            # Azure OpenAI SDK
anthropic>=0.20.0               # Claude SDK
google-generativeai>=0.3.0      # Gemini SDK
```

### 7. 环境配置示例 (`.env.example`)

完整的多提供商配置模板，涵盖所有 4 个提供商。

### 8. 综合文档 (`docs/MULTI_PROVIDER_GUIDE.md`)

详细的多提供商使用指南，包含：
- 环境变量配置
- API 密钥获取方法
- 依赖安装步骤
- 使用示例代码
- 性能对比
- 成本估算
- 故障排查

### 9. 示例脚本

#### `examples/example_azure.py`
演示 Azure OpenAI 的使用，包括：
- 基本数据提取
- 长文档处理
- 连接验证

#### `examples/example_claude.py`
演示 Claude 的使用，包括：
- 基本信息提取
- 长文档处理（利用 200K token 上下文）
- 复杂推理示例
- 模型成本对比

#### `examples/example_gemini.py`
演示 Gemini 的使用，包括：
- 基本数据提取
- 多模态能力说明
- 成本高效的应用
- 性能特点分析
- 大规模应用成本估算

#### `examples/example_multi_provider.py`
多提供商对比工具：
- 基本数据提取对比
- 复杂文档处理对比
- 速度、准确性、成本对比
- 详细的性能报告

## 使用方式

### 方式 1：通过环境变量（应用启动时）

```bash
# .env 文件
LLM_PROVIDER=claude
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxx
```

然后启动应用，所有请求都将使用 Claude。

### 方式 2：通过 API 请求（运行时切换）

```bash
curl -X POST http://localhost:8000/api/v1/extract \
  -H "Content-Type: application/json" \
  -d '{
    "source": "raw",
    "file": "待提取的文本",
    "provider": "gemini",
    "model": "gemini-2.0-flash",
    "schema": [...]
  }'
```

### 方式 3：在 Python 代码中

```python
from app.llm import LLMFactory

# 使用不同提供商
llm_openai = LLMFactory.create("openai")
llm_claude = LLMFactory.create("claude")
llm_gemini = LLMFactory.create("gemini")

# 获取可用模型
models = llm_claude.get_available_models()
for model in models:
    print(f"{model.name}: {model.display_name}")

# 验证连接
is_connected = await llm_gemini.validate_connection()

# 执行提取
result = await llm_claude.extract(
    content=text,
    schema=schema,
    model="claude-3-opus-20240229"
)
```

## 系统架构

```
┌─────────────────────────────────────────────────────┐
│              FastAPI Application                    │
├─────────────────────────────────────────────────────┤
│  API Routes (routes.py)                            │
│  - 接收 provider 参数                               │
│  - 支持运行时提供商切换                              │
├─────────────────────────────────────────────────────┤
│  Extract Service (extract_service.py)               │
│  - 业务逻辑编排                                     │
│  - 调用 LLMFactory                                  │
├─────────────────────────────────────────────────────┤
│  LLM Factory (factory.py)                           │
│  - 根据 provider 参数创建实例                        │
│  - 支持新提供商注册                                 │
├─────────────────────────────────────────────────────┤
│  LLM Implementations                                │
│  ├─ BaseLLM (base.py)                              │
│  │  - 定义通用接口                                  │
│  │  - 提供通用工具方法                              │
│  ├─ OpenAILLM (openai_llm.py)                      │
│  ├─ AzureOpenAILLM (azure_openai_llm.py)           │
│  ├─ ClaudeLLM (claude_llm.py)                      │
│  └─ GeminiLLM (gemini_llm.py)                      │
└─────────────────────────────────────────────────────┘
```

## 支持的模型列表

### OpenAI
- gpt-4o
- gpt-4o-mini
- gpt-4-turbo
- gpt-3.5-turbo

### Azure OpenAI
- gpt-4-deployment
- gpt-4o-deployment
- gpt-4-turbo-deployment

### Anthropic Claude
- claude-3-opus-20240229 (最强大)
- claude-3-sonnet-20240229 (推荐)
- claude-3-haiku-20240307 (最快最便宜)

### Google Gemini
- gemini-2.0-flash (最新最快)
- gemini-1.5-pro (高性能)
- gemini-1.5-flash (经济型)

## 性能对比

| 指标 | OpenAI | Azure | Claude | Gemini |
|------|--------|-------|--------|--------|
| 速度 | 快 | 快 | 快 | 很快 |
| 准确性 | 很高 | 很高 | 很高 | 高 |
| 成本 | 中 | 中 | 低 | 很低 |
| 上下文 | 128K | 128K | 200K | 100K+ |
| 多模态 | 有 | 有 | 部分 | 有 |
| 推荐场景 | 通用 | 企业 | 推理 | 成本敏感 |

## 迁移指南

如果之前使用的是单一 OpenAI 提供商，现在可以：

### 1. 无需修改代码
所有请求默认仍使用 OpenAI，完全向后兼容。

### 2. 逐步迁移
可以在 API 请求中添加 `provider` 参数，部分流量迁移到新提供商：
```json
{
  "provider": "claude",
  "model": "claude-3-sonnet-20240229",
  ...
}
```

### 3. 完全切换
修改 `.env` 文件中的 `LLM_PROVIDER` 值，完全切换到新提供商。

## 常见问题

### Q: 哪个提供商最便宜？
**A:** Gemini 是最便宜的选择，成本比 GPT-4 低 80%+ 以上。

### Q: 哪个提供商最快？
**A:** Gemini 2.0 Flash 是最快的，平均响应时间 < 500ms。

### Q: 哪个提供商最强大？
**A:** 推理能力：Claude Opus；通用能力：OpenAI GPT-4o。

### Q: 能同时使用多个提供商吗？
**A:** 可以，通过 API 请求时指定 `provider` 参数即可。

### Q: 添加新提供商有多复杂？
**A:** 很简单，只需继承 `BaseLLM` 类并实现 3 个方法，然后在 factory 中注册。

## 下一步

### 短期计划
- [ ] 添加更多提供商支持（Ollama、Mistral 等）
- [ ] 优化模型选择策略
- [ ] 添加成本追踪功能
- [ ] 实现负载均衡

### 中期计划
- [ ] 支持多模式推理（text+image）
- [ ] 实现流式响应
- [ ] 添加请求重试机制
- [ ] 支持模型微调

### 长期计划
- [ ] 本地模型集成（Ollama）
- [ ] 多模型集合推理
- [ ] 自适应模型选择
- [ ] AI 成本优化建议

## 技术栈更新

| 组件 | 版本 | 更新 |
|------|------|------|
| FastAPI | 0.104.1 | - |
| OpenAI | 1.3.0 | 保持 |
| Azure OpenAI | 1.10.0+ | 新增 |
| Anthropic | 0.20.0+ | 新增 |
| Google Generative AI | 0.3.0+ | 新增 |
| Pydantic | 2.5.0 | - |

## 相关文件清单

### 核心实现
- [x] `app/llm/base.py` - 基础接口（增强）
- [x] `app/llm/azure_openai_llm.py` - Azure 实现（新增）
- [x] `app/llm/claude_llm.py` - Claude 实现（新增）
- [x] `app/llm/gemini_llm.py` - Gemini 实现（新增）
- [x] `app/llm/factory.py` - 工厂类（更新）

### 配置和模型
- [x] `app/core/config.py` - 配置（增强）
- [x] `app/models/schemas.py` - 数据模型（更新）
- [x] `.env.example` - 环境配置（更新）

### 服务层
- [x] `app/services/extract_service.py` - 提取服务（更新）
- [x] `app/api/routes.py` - API 路由（文档更新）

### 文档和示例
- [x] `docs/MULTI_PROVIDER_GUIDE.md` - 多提供商指南（新增）
- [x] `examples/example_azure.py` - Azure 示例（新增）
- [x] `examples/example_claude.py` - Claude 示例（新增）
- [x] `examples/example_gemini.py` - Gemini 示例（新增）
- [x] `examples/example_multi_provider.py` - 对比示例（新增）
- [x] `requirements.txt` - 依赖（更新）

## 测试建议

### 单元测试
```bash
pytest tests/llm/test_azure_openai.py
pytest tests/llm/test_claude.py
pytest tests/llm/test_gemini.py
```

### 集成测试
```bash
python examples/example_multi_provider.py
```

### 性能测试
```bash
python examples/benchmark.py  # 需要创建
```

## 支持和反馈

如有问题或建议，请：
1. 查阅 `docs/MULTI_PROVIDER_GUIDE.md`
2. 查看相关示例脚本
3. 检查日志输出获取详细错误信息
4. 提交 Issue 到项目仓库

## 总结

此次更新使项目从单一 OpenAI 提供商升级到支持 4 个主要 LLM 提供商的灵活架构。用户现在可以：

✓ 在不同提供商间灵活切换  
✓ 根据需求选择最适合的模型  
✓ 优化成本和性能的平衡  
✓ 轻松添加新的提供商支持  
✓ 充分利用各提供商的独特优势  

系统保持向后兼容，现有代码无需修改即可继续工作。
