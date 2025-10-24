# 所有 LLM 提供商对比和快速选择指南

## 提供商概览

| 提供商 | 类型 | 部署方式 | 成本 | 推荐场景 |
|--------|------|---------|------|---------|
| **OpenAI** | 云服务 | API 调用 | 按使用量付费 | 生产环境、准确性优先 |
| **Azure OpenAI** | 云服务 | API 调用 | 按使用量付费 | 企业级、需要 Azure 集成 |
| **Claude** | 云服务 | API 调用 | 按使用量付费 | 复杂任务、长上下文 |
| **Gemini** | 云服务 | API 调用 | 按使用量付费 | 多模态、实时数据 |
| **Custom (本地)** | 开源/本地 | 自托管 | 零成本 | 离线使用、隐私保护、定制化 |

## 详细对比

### 1. OpenAI

**优点：**
- ✅ 最成熟的 API
- ✅ 模型质量最高
- ✅ 广泛的生态支持
- ✅ 实时更新和改进

**缺点：**
- ❌ 成本最高
- ❌ 需要网络连接
- ❌ API 速率限制

**配置：**
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
```

**使用场景：**
- 需要最高准确性的生产系统
- 企业级应用
- 复杂的数据提取任务

### 2. Azure OpenAI

**优点：**
- ✅ 与 Azure 生态集成
- ✅ 企业级 SLA
- ✅ 区域部署选项
- ✅ 与 Microsoft 产品集成

**缺点：**
- ❌ 需要 Azure 订阅
- ❌ 配置复杂
- ❌ 地区限制

**配置：**
```env
LLM_PROVIDER=azure
AZURE_OPENAI_KEY=...
AZURE_OPENAI_ENDPOINT=https://xxx.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=...
```

**使用场景：**
- Azure 企业客户
- 需要特定地区部署
- 需要 SLA 保证

### 3. Claude (Anthropic)

**优点：**
- ✅ 长上下文支持 (100K+ tokens)
- ✅ 优秀的推理能力
- ✅ 低率限制
- ✅ 更好的隐私保护

**缺点：**
- ❌ 速度较慢
- ❌ 生态支持不如 OpenAI
- ❌ 成本相对较高

**配置：**
```env
LLM_PROVIDER=claude
ANTHROPIC_API_KEY=...
CLAUDE_MODEL=claude-3-sonnet-20240229
```

**使用场景：**
- 需要长上下文的应用
- 复杂的分析和推理
- 隐私敏感的应用

### 4. Gemini (Google)

**优点：**
- ✅ 多模态能力
- ✅ 与 Google 服务集成
- ✅ 竞争力的价格
- ✅ 快速的响应

**缺点：**
- ❌ API 稳定性还在改进
- ❌ 文档相对不完善
- ❌ 生态支持较少

**配置：**
```env
LLM_PROVIDER=gemini
GOOGLE_API_KEY=...
GEMINI_MODEL=gemini-2.0-flash
```

**使用场景**
- 需要多模态能力
- Google Cloud 用户
- 对成本敏感

### 5. Custom (OpenAI 兼容本地服务)

**优点：**
- ✅ 完全离线，无需网络
- ✅ 零成本（除了硬件）
- ✅ 完整的隐私保护
- ✅ 可自定义模型

**缺点：**
- ❌ 需要本地硬件（GPU/CPU）
- ❌ 模型质量参差不齐
- ❌ 需要维护和更新
- ❌ 初始设置复杂

**配置：**
```env
LLM_PROVIDER=custom
CUSTOM_BASE_URL=http://localhost:1234/v1
CUSTOM_MODEL=neural-chat
```

**使用场景：**
- 完全离线应用
- 隐私敏感的应用
- 大规模部署（降低成本）
- 边缘计算

**支持的本地服务：**
- LM Studio - 易用的 GUI
- Ollama - 轻量级、跨平台
- vLLM - 高性能推理
- LocalAI - 完整的 OpenAI 替代品

## 快速选择指南

### 选择决策树

```
您需要生产级的准确性吗？
├─ 是 → OpenAI 或 Azure OpenAI
└─ 否 →
    您需要离线使用吗？
    ├─ 是 → Custom (本地服务)
    └─ 否 →
        您需要长上下文吗？
        ├─ 是 → Claude
        └─ 否 →
            您需要多模态吗？
            ├─ 是 → Gemini
            └─ 否 → Claude 或 OpenAI
```

### 成本对比（美元 / 100 万 tokens）

| 提供商 | 输入成本 | 输出成本 | 总体等级 |
|--------|---------|---------|---------|
| OpenAI (GPT-3.5) | $0.50 | $1.50 | ⭐⭐⭐ |
| OpenAI (GPT-4) | $30 | $60 | ⭐ |
| Azure OpenAI | $1.50 | $2.00 | ⭐⭐ |
| Claude 3.5 Sonnet | $3.00 | $15.00 | ⭐⭐ |
| Gemini | $0.50 | $2.00 | ⭐⭐⭐ |
| Custom (本地) | $0 | $0 | ⭐⭐⭐⭐⭐ |

### 性能对比（相对评分）

| 提供商 | 准确性 | 速度 | 稳定性 | 支持 | 总分 |
|--------|-------|------|--------|------|------|
| OpenAI | 🟦🟦🟦🟦🟩 | 🟩🟩🟩🟩🟩 | 🟦🟦🟦🟦🟩 | 🟦🟦🟦🟦🟩 | 92/100 |
| Azure | 🟦🟦🟦🟦🟩 | 🟩🟩🟩🟩🟩 | 🟦🟦🟦🟦🟦 | 🟦🟦🟦🟩🟩 | 88/100 |
| Claude | 🟦🟦🟦🟦🟦 | 🟩🟩🟩🟩🟩 | 🟦🟦🟦🟩🟩 | 🟩🟩🟩🟩🟩 | 92/100 |
| Gemini | 🟦🟦🟦🟩🟩 | 🟦🟦🟦🟦🟦 | 🟦🟦🟦🟩🟩 | 🟩🟩🟩🟩🟩 | 82/100 |
| Custom | 🟩🟩🟩🟩🟩 | 🟩🟩🟩🟩🟩 | 🟩🟩🟩🟩🟩 | 🟩🟩🟩🟩🟩 | 无限制* |

*取决于所用模型的质量

## 集成示例

### 使用 OpenAI

```python
request = ExtractRequest(
    source="raw",
    file="your text",
    provider="openai",
    model="gpt-4o-mini",
    schema=[...]
)
```

### 使用 Azure OpenAI

```python
request = ExtractRequest(
    source="raw",
    file="your text",
    provider="azure",
    model="gpt-4",
    schema=[...]
)
```

### 使用 Claude

```python
request = ExtractRequest(
    source="raw",
    file="your text",
    provider="claude",
    model="claude-3-sonnet-20240229",
    schema=[...]
)
```

### 使用 Gemini

```python
request = ExtractRequest(
    source="raw",
    file="your text",
    provider="gemini",
    model="gemini-2.0-flash",
    schema=[...]
)
```

### 使用本地 LM Studio

```python
request = ExtractRequest(
    source="raw",
    file="your text",
    provider="custom",
    model="neural-chat",
    custom_base_url="http://localhost:1234/v1",
    custom_api_key="not-needed",
    schema=[...]
)
```

### 使用本地 Ollama

```python
request = ExtractRequest(
    source="raw",
    file="your text",
    provider="custom",
    model="llama2",
    custom_base_url="http://localhost:11434/v1",
    custom_api_key="not-needed",
    schema=[...]
)
```

## 环境配置快速参考

### 开发环境（推荐使用本地 LLM）

```env
LLM_PROVIDER=custom
CUSTOM_BASE_URL=http://localhost:1234/v1
CUSTOM_API_KEY=not-needed
CUSTOM_MODEL=neural-chat
```

### 测试环境（推荐使用 OpenAI）

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-test-...
OPENAI_MODEL=gpt-4o-mini
```

### 生产环境（推荐使用 Azure 或 OpenAI）

```env
LLM_PROVIDER=azure
AZURE_OPENAI_KEY=...
AZURE_OPENAI_ENDPOINT=...
AZURE_OPENAI_DEPLOYMENT=...
```

## 迁移指南

### 从 OpenAI 迁移到本地 LLM

1. **安装本地服务**
   ```bash
   # 使用 Ollama
   brew install ollama
   ollama pull llama2
   ```

2. **更新配置**
   ```env
   LLM_PROVIDER=custom
   CUSTOM_BASE_URL=http://localhost:11434/v1
   CUSTOM_MODEL=llama2
   ```

3. **测试**
   ```bash
   python examples/example_custom_openai_compatible.py
   ```

### 从一个云提供商迁移到另一个

由于 API 定义相似，您只需要更改配置文件和环境变量，无需修改代码。

```env
# 从 OpenAI 迁移到 Claude
LLM_PROVIDER=claude
ANTHROPIC_API_KEY=...
CLAUDE_MODEL=claude-3-sonnet-20240229
```

## 常见问题

**Q: 哪个提供商成本最低？**
A: 本地 LLM 提供商（Custom）的成本最低（仅硬件成本），其次是 Gemini 和 OpenAI（GPT-3.5）。

**Q: 哪个提供商速度最快？**
A: OpenAI 通常速度最快，其次是 Gemini，本地 LLM 取决于硬件。

**Q: 如何在提供商之间切换？**
A: 只需更改 `LLM_PROVIDER` 环境变量和相应的 API 密钥。

**Q: 可以同时使用多个提供商吗？**
A: 可以。在请求时指定 `provider` 参数。

**Q: 本地 LLM 真的能离线工作吗？**
A: 是的，安装后完全离线工作，无需互联网连接。

## 下一步

- 详细了解 [OpenAI 提供商](/docs/PROVIDERS_OPENAI.md)
- 详细了解 [Azure 提供商](/docs/PROVIDERS_AZURE.md)
- 详细了解 [Claude 提供商](/docs/PROVIDERS_CLAUDE.md)
- 详细了解 [Gemini 提供商](/docs/PROVIDERS_GEMINI.md)
- 详细了解 [Custom 提供商](/docs/CUSTOM_LLM_PROVIDERS.md)
