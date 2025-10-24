# 迭代更新日志 - Custom (OpenAI 兼容) LLM 提供商

**日期**: 2024年10月24日
**版本**: 1.1.0

## 新增功能

### 1. Custom OpenAI 兼容提供商 ✨

添加了对任何兼容 OpenAI API 的本地或远程 LLM 服务的支持。

**特性:**
- 支持本地部署的 LLM 模型（零成本）
- 完全离线工作，无需互联网连接
- 支持多个流行的本地 LLM 框架
- 完整的隐私保护
- 可自定义的模型和参数

**支持的本地 LLM 服务:**
- LM Studio - 易用的 GUI 应用
- Ollama - 轻量级跨平台框架
- vLLM - 高性能推理引擎
- LocalAI - OpenAI API 替代品

### 2. 核心代码更改

#### 新文件

| 文件 | 说明 |
|------|------|
| `app/llm/openai_compatible_llm.py` | Custom 提供商实现 (270 行) |
| `docs/CUSTOM_LLM_PROVIDERS.md` | Custom 提供商详细文档 |
| `docs/LLM_PROVIDERS_GUIDE.md` | 所有提供商对比和选择指南 |
| `examples/example_custom_openai_compatible.py` | Custom 提供商使用示例 |

#### 修改文件

| 文件 | 更改 |
|------|------|
| `app/llm/factory.py` | 添加 custom 提供商注册和参数支持 |
| `app/core/config.py` | 添加 CUSTOM_BASE_URL、CUSTOM_API_KEY、CUSTOM_MODEL 配置 |
| `app/models/schemas.py` | 在 ExtractRequest 中添加 custom 提供商参数 |
| `app/services/extract_service.py` | 更新提取逻辑以支持 custom 提供商参数 |
| `.env.example` | 添加 custom 提供商配置示例 |
| `requirements.txt` | 已包含必要的依赖（无新增） |

## API 变更

### ExtractRequest 新参数

```python
provider: Literal["openai", "azure", "claude", "gemini", "custom"]
custom_base_url: Optional[str]  # Custom 提供商的 API 基础 URL
custom_api_key: Optional[str]   # Custom 提供商的 API 密钥（可选）
```

### 请求示例

**基础请求（使用 LM Studio）:**
```json
{
  "source": "raw",
  "file": "张三是工程师，出生于1990年",
  "provider": "custom",
  "custom_base_url": "http://localhost:1234/v1",
  "model": "neural-chat",
  "schema": [...]
}
```

**使用本地 Ollama:**
```json
{
  "source": "raw",
  "file": "...",
  "provider": "custom",
  "custom_base_url": "http://localhost:11434/v1",
  "model": "llama2",
  "schema": [...]
}
```

## 配置示例

### .env 文件配置

```bash
# 使用本地 LM Studio
LLM_PROVIDER=custom
CUSTOM_BASE_URL=http://localhost:1234/v1
CUSTOM_API_KEY=not-needed
CUSTOM_MODEL=neural-chat

# 使用本地 Ollama
# LLM_PROVIDER=custom
# CUSTOM_BASE_URL=http://localhost:11434/v1
# CUSTOM_API_KEY=not-needed
# CUSTOM_MODEL=llama2

# 使用远程 OpenAI 兼容服务
# LLM_PROVIDER=custom
# CUSTOM_BASE_URL=https://api.example.com/v1
# CUSTOM_API_KEY=your-api-key
# CUSTOM_MODEL=your-model
```

## 使用指南

### 快速开始

1. **安装本地 LLM 服务**
   ```bash
   # 使用 Ollama（推荐）
   brew install ollama
   ollama pull llama2
   ollama serve
   ```

2. **配置 .env**
   ```bash
   LLM_PROVIDER=custom
   CUSTOM_BASE_URL=http://localhost:11434/v1
   CUSTOM_MODEL=llama2
   ```

3. **运行示例**
   ```bash
   python examples/example_custom_openai_compatible.py
   ```

### 本地服务设置指南

详见：`docs/CUSTOM_LLM_PROVIDERS.md`

包括以下服务的完整设置指南：
- LM Studio
- Ollama
- vLLM
- LocalAI

## 功能对比

### 现在支持的提供商

| 提供商 | 推理 | 微调 | 离线 | 成本 |
|--------|------|------|------|------|
| OpenAI | ✅ | ❌ | ❌ | 中高 |
| Azure | ✅ | ❌ | ❌ | 中高 |
| Claude | ✅ | ❌ | ❌ | 中 |
| Gemini | ✅ | ❌ | ❌ | 中 |
| Custom | ✅ | ✅ | ✅ | 零 |

## 文档

### 新增文档

- **CUSTOM_LLM_PROVIDERS.md** - Custom 提供商完整文档
  - 4 个本地服务的详细设置指南
  - 故障排除和优化建议
  - 生产使用建议

- **LLM_PROVIDERS_GUIDE.md** - 所有提供商对比指南
  - 5 个提供商的详细对比
  - 快速选择决策树
  - 成本对比表
  - 性能对比表
  - 迁移指南

### 示例代码

- **example_custom_openai_compatible.py** - Custom 提供商示例
  - 4 个不同本地服务的使用示例
  - 包括 LM Studio、Ollama、vLLM、LocalAI
  - 完整的错误处理

## 性能指标

### 本地 LLM 性能（参考值）

| 模型 | 响应时间 | 准确性 | 内存占用 |
|------|---------|-------|---------|
| Llama 2 7B | 1-3秒 | 中等 | 14GB |
| Mistral 7B | 1-2秒 | 较高 | 14GB |
| Neural Chat 7B | 1-2秒 | 中等 | 14GB |
| Phi 2.7B | 0.5-1秒 | 一般 | 5GB |

*注: 性能取决于硬件配置*

## 向后兼容性

✅ **完全向后兼容** - 现有代码无需修改，只需更新配置文件

### 迁移 checklist

- [ ] 更新 `.env` 或环境变量
- [ ] 可选：为 custom 提供商配置本地 LLM 服务
- [ ] 测试现有的 API 调用
- [ ] 更新文档（如适用）
- [ ] 可选：在 CI/CD 流程中测试新提供商

## 已知限制

1. **本地 LLM 准确性** - 本地模型的准确性可能低于云服务
2. **硬件要求** - 需要足够的 CPU/GPU 和内存
3. **模型维护** - 需要手动更新和维护本地模型
4. **首次启动时间** - 加载大型模型需要时间

## 下一步计划

- [ ] 支持更多本地 LLM 框架（Text Generation WebUI、Hugging Face、etc）
- [ ] 添加模型缓存和预加载机制
- [ ] 性能监控和指标收集
- [ ] 支持模型微调接口
- [ ] 集成 NVIDIA TensorRT 优化

## 贡献指南

欢迎贡献！可以通过以下方式参与：

1. 报告 bug
2. 提建议
3. 提交 PR
4. 改进文档
5. 分享最佳实践

## 支持和反馈

如有问题或建议，请：

1. 查阅 [FAQ 文档](./CUSTOM_LLM_PROVIDERS.md#故障排除)
2. 检查 [提供商对比指南](./LLM_PROVIDERS_GUIDE.md)
3. 查看 [示例代码](./examples/example_custom_openai_compatible.py)
4. 提交 Issue 或 PR

## 致谢

感谢以下开源项目的支持：
- **Ollama** - 简化的 LLM 框架
- **vLLM** - 高性能推理引擎
- **LocalAI** - OpenAI API 替代品
- **LM Studio** - 易用的 LLM IDE

## 版本信息

- **版本**: 1.1.0
- **发布日期**: 2024-10-24
- **Python**: 3.8+
- **状态**: 稳定版

## 更新摘要

✨ **主要亮点:**
- 🎯 完整的本地 LLM 支持
- 🚀 零成本的推理引擎
- 🔒 完整的离线和隐私支持
- 📚 详细的文档和示例
- 🔄 完全向后兼容

🎉 感谢使用 LLM Document Parser！
