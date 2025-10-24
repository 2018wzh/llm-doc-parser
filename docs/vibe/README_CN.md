# LLM Document Parser 🚀

一个优化的 FastAPI 应用程序，用于从 MinIO 下载文件（或处理原始文本），使用 Unstructured 库提取文本，然后通过 OpenAI LLM 将内容转换为指定 schema 的 JSON。

## 🎯 核心功能

- **多源支持**: MinIO 对象存储和原始文本
- **多格式处理**: PDF、DOCX、XLSX、TXT 等（通过 Unstructured）
- **LLM 集成**: OpenAI API（支持工厂模式扩展）
- **优化 Prompt**: Few-shot learning 和清晰的指令设计
- **数据提取**: 自动类型转换和验证
- **异步优先**: 高性能异步架构
- **完整文档**: 快速开始、架构设计、开发指南等

## ⚡ 快速开始 (5 分钟)

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置环境
```bash
cp .env.example .env
# 编辑 .env，填入您的 OPENAI_API_KEY
```

### 3. 启动应用
```bash
python run.py
```

### 4. 测试 API
访问 Swagger UI: http://localhost:8000/docs

## 📚 文档

| 文档 | 说明 |
|------|------|
| [QUICKSTART.md](QUICKSTART.md) | ⭐ 5分钟快速开始（推荐先看这个） |
| [APP_README.md](APP_README.md) | 完整功能文档和 API 参考 |
| [ARCHITECTURE.md](ARCHITECTURE.md) | 系统架构和设计模式 |
| [DEVELOPMENT.md](DEVELOPMENT.md) | 开发环境和扩展指南 |
| [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) | 项目总结和特性列表 |
| [INDEX.md](INDEX.md) | 资源导航索引 |
| [COMPLETION_REPORT.md](COMPLETION_REPORT.md) | 项目完成报告 |

## 🔥 API 示例

### 从原始文本提取数据

```bash
curl -X POST "http://localhost:8000/api/v1/extract" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "raw",
    "file": "张三，35岁，是一名高级工程师",
    "schema": [
      {
        "name": "姓名",
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
        "name": "职位",
        "field": "position",
        "type": "text",
        "required": false
      }
    ]
  }'
```

### 响应示例

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
      "value": 35
    },
    {
      "field": "position",
      "type": "text",
      "value": "高级工程师"
    }
  ],
  "code": "200",
  "message": "Success"
}
```

## 🏗️ 项目结构

```
llm-doc-parser/
├── app/                    # 应用源代码
│   ├── api/               # API 路由
│   ├── core/              # 配置和异常
│   ├── models/            # 数据模型
│   ├── llm/               # LLM 工厂和实现
│   ├── services/          # 业务逻辑
│   └── main.py            # FastAPI 应用
├── tests/                 # 测试代码
├── requirements.txt       # 依赖
├── Dockerfile             # Docker 镜像
├── docker-compose.yml     # Docker Compose
├── run.py                 # 启动脚本
├── example.py             # 使用示例
└── 文档文件               # README、QUICKSTART等
```

## ✨ 核心特性

### 1. 工厂模式 LLM 设计
```python
# 轻松切换或扩展 LLM 提供商
llm = LLMFactory.create("openai")
LLMFactory.register("claude", ClaudeLLM)
```

### 2. 优化的 Prompt 设计
- 清晰的任务描述
- 结构化 Schema 定义
- Few-shot learning 示例
- 类型约束和边界处理

### 3. 分层架构
- API 层：FastAPI 路由
- Service 层：业务逻辑
- LLM 层：模型集成
- Utility 层：工具服务

### 4. 完整的异常处理
- 自定义异常体系
- 统一的错误响应
- 详细的日志记录

## 🚀 部署

### Docker Compose (推荐)
```bash
docker-compose up -d
```

### Docker
```bash
docker build -t llm-parser .
docker run -p 8000:8000 --env-file .env llm-parser
```

### 生产环境
```bash
gunicorn -w 4 -b 0.0.0.0:8000 app.main:app
```

## 🧪 测试

```bash
# 运行所有测试
pytest tests/ -v

# 项目验证
python verify_project.py

# 查看示例
python example.py
```

## 📊 技术栈

- **Web**: FastAPI 0.104+
- **LLM**: OpenAI 1.3+
- **文件处理**: Unstructured 0.10+
- **存储**: MinIO 7.2+
- **验证**: Pydantic 2.5+
- **测试**: Pytest 7.0+
- **容器**: Docker 20.10+

## 🔐 安全

- ✅ 环境变量管理密钥
- ✅ Pydantic 输入验证
- ✅ 完整的异常处理
- ✅ 日志脱敏
- ✅ CORS 配置
- ✅ 健康检查

## 📈 性能

- ✅ 全异步实现
- ✅ 连接池管理
- ✅ 结构化日志
- ✅ 容器友好
- ✅ 高并发支持

## 🎓 学习资源

- **新手**: 从 [QUICKSTART.md](QUICKSTART.md) 开始
- **开发**: 查看 [DEVELOPMENT.md](DEVELOPMENT.md)
- **架构**: 阅读 [ARCHITECTURE.md](ARCHITECTURE.md)
- **API**: 访问 http://localhost:8000/docs
- **示例**: 运行 `python example.py`

## 💡 常见问题

**Q: 如何添加新的 LLM 提供商？**
A: 创建类继承 `BaseLLM`，然后用 `LLMFactory.register()` 注册。详见 [DEVELOPMENT.md](DEVELOPMENT.md)

**Q: 如何从 MinIO 提取文件？**
A: 将 `source` 设置为 `"minio"` 并提供文件 URL。详见 [QUICKSTART.md](QUICKSTART.md)

**Q: 如何提高提取准确度？**
A: 优化 Schema 描述、选择更好的模型、提供更多上下文。详见 [QUICKSTART.md](QUICKSTART.md)

## 📞 反馈与支持

- 📖 完整文档: 查看各 README 文件
- 💬 API 文档: http://localhost:8000/docs
- 🐛 问题反馈: 提交 GitHub Issue

## 📄 许可证

MIT License

## 🎉 致谢

感谢使用 LLM Document Parser！

---

**版本**: 1.0.0  
**最后更新**: 2024 年 10 月 24 日  
**项目状态**: ✅ 完成并可用于生产

👉 **立即开始**: [查看快速开始指南](QUICKSTART.md)
