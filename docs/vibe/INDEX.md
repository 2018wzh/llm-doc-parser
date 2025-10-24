# 📚 LLM Document Parser - 资源索引

## 🎯 快速导航

### 📖 文档

| 文档 | 描述 | 适合人群 |
|------|------|--------|
| [快速开始](QUICKSTART.md) | 5 分钟快速上手指南 | 所有人 |
| [完整文档](APP_README.md) | 详细的功能和 API 说明 | 使用者 |
| [架构设计](ARCHITECTURE.md) | 系统架构和设计模式 | 开发者 |
| [开发指南](DEVELOPMENT.md) | 开发环境和最佳实践 | 贡献者 |
| [项目总结](PROJECT_SUMMARY.md) | 项目概览和特性总结 | 评估者 |

### 🔧 配置和启动

| 文件 | 用途 |
|------|------|
| [.env.example](.env.example) | 环境变量示例 |
| [requirements.txt](requirements.txt) | Python 依赖 |
| [Dockerfile](Dockerfile) | Docker 镜像构建 |
| [docker-compose.yml](docker-compose.yml) | Docker Compose 配置 |
| [pytest.ini](pytest.ini) | Pytest 测试配置 |

### 🐍 代码文件

#### 核心模块 (app/core/)
- `config.py` - 应用配置管理
- `exceptions.py` - 自定义异常定义

#### 数据模型 (app/models/)
- `schemas.py` - Pydantic 数据模型

#### LLM 层 (app/llm/)
- `base.py` - LLM 基础接口
- `openai_llm.py` - OpenAI 实现
- `factory.py` - 工厂模式实现

#### 业务逻辑 (app/services/)
- `extract_service.py` - 主业务服务
- `minio_service.py` - MinIO 文件服务
- `file_service.py` - 文件处理服务

#### API 层 (app/api/)
- `routes.py` - API 路由定义

#### 主应用 (app/)
- `main.py` - FastAPI 应用

#### 测试 (tests/)
- `test_api.py` - API 测试用例

### 🚀 启动脚本

| 脚本 | 用途 |
|------|------|
| [run.py](run.py) | 启动开发服务器 |
| [example.py](example.py) | 使用示例脚本 |
| [verify_project.py](verify_project.py) | 项目验证脚本 |

## 📊 项目概览

```
LLM Document Parser
├── 数据来源
│   ├── MinIO 对象存储
│   └── 原始文本
├── 文件处理
│   └── Unstructured 库支持多种格式
├── LLM 处理
│   ├── OpenAI API（支持扩展）
│   └── 优化的 Prompt 设计
└── 数据输出
    └── 结构化 JSON
```

## 🎯 核心特性

- ✅ **多源支持**: MinIO 和原始文本
- ✅ **工厂模式**: 易于扩展的 LLM 实现
- ✅ **优化 Prompt**: Few-shot learning 设计
- ✅ **类型转换**: 自动数据类型转换
- ✅ **异常处理**: 完善的错误处理
- ✅ **异步优先**: 全异步实现
- ✅ **API 文档**: Swagger/ReDoc 支持

## 📈 快速开始路径

### 新手用户
1. 阅读 [快速开始](QUICKSTART.md)
2. 复制 `.env.example` 到 `.env`
3. 运行 `python run.py`
4. 访问 http://localhost:8000/docs

### 开发者
1. 阅读 [开发指南](DEVELOPMENT.md)
2. 查看 [架构设计](ARCHITECTURE.md)
3. 运行 `python verify_project.py` 验证项目
4. 运行 `pytest tests/ -v` 测试
5. 查看 [example.py](example.py) 了解用法

### 部署者
1. 查看 [完整文档](APP_README.md) 的部署章节
2. 使用 [docker-compose.yml](docker-compose.yml)
3. 或使用 [Dockerfile](Dockerfile) 构建镜像
4. 配置环境变量 `.env`

## 🔑 关键概念

### 分层架构

```
HTTP Request
    ↓
API Layer (routes.py)
    ↓
Service Layer (extract_service.py)
    ↓
├─ MinIO Service (download)
├─ File Service (extract text)
└─ LLM Layer (extract data)
    ↓
HTTP Response
```

### 工厂模式

```python
# 创建 LLM 实例
llm = LLMFactory.create("openai")

# 扩展新的提供商
LLMFactory.register("claude", ClaudeLLM)
```

### Prompt 优化

```
系统提示 (系统角色和任务)
+ Schema 定义 (清晰的字段说明)
+ 输出示例 (Few-shot learning)
+ 特殊说明 (边界情况处理)
= 优化的 Prompt
```

## 📚 学习资源

### FastAPI
- [官方文档](https://fastapi.tiangolo.com/)
- [入门教程](https://fastapi.tiangolo.com/tutorial/)

### OpenAI API
- [API 文档](https://platform.openai.com/docs)
- [API 参考](https://platform.openai.com/docs/api-reference)

### 设计模式
- [工厂模式](https://refactoring.guru/design-patterns/factory-method)
- [依赖注入](https://en.wikipedia.org/wiki/Dependency_injection)

## 🧪 测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试
pytest tests/test_api.py::test_health_check -v

# 生成覆盖率
pytest tests/ --cov=app --cov-report=html
```

## 🐳 Docker

```bash
# 使用 Docker Compose（推荐）
docker-compose up -d

# 或手动构建和运行
docker build -t llm-parser .
docker run -p 8000:8000 --env-file .env llm-parser
```

## 📞 常见问题

### 如何添加新的 LLM 提供商？
→ 查看 [开发指南](DEVELOPMENT.md) 的"扩展开发"部分

### 如何提高提取准确度？
→ 查看 [快速开始](QUICKSTART.md) 的"常见问题"部分

### 如何处理大文件？
→ 查看 [完整文档](APP_README.md) 的"常见问题"部分

### 项目结构是否完整？
→ 运行 `python verify_project.py`

## 🔐 安全提示

⚠️ **重要**:
1. 不要在代码中硬编码 API 密钥
2. 使用环境变量存储敏感信息
3. 不要将 `.env` 文件提交到版本控制
4. 生产环境使用 HTTPS
5. 定期轮换 API 密钥

## 📝 文件清单

### 配置文件 (5 个)
- ✅ .env.example
- ✅ requirements.txt
- ✅ Dockerfile
- ✅ docker-compose.yml
- ✅ pytest.ini

### Python 文件 (14 个)
- ✅ app/__init__.py
- ✅ app/main.py
- ✅ app/core/__init__.py
- ✅ app/core/config.py
- ✅ app/core/exceptions.py
- ✅ app/models/__init__.py
- ✅ app/models/schemas.py
- ✅ app/llm/__init__.py
- ✅ app/llm/base.py
- ✅ app/llm/openai_llm.py
- ✅ app/llm/factory.py
- ✅ app/services/__init__.py
- ✅ app/services/minio_service.py
- ✅ app/services/file_service.py
- ✅ app/services/extract_service.py
- ✅ app/api/__init__.py
- ✅ app/api/routes.py
- ✅ tests/__init__.py
- ✅ tests/test_api.py

### 脚本文件 (3 个)
- ✅ run.py
- ✅ example.py
- ✅ verify_project.py

### 文档文件 (6 个)
- ✅ QUICKSTART.md
- ✅ APP_README.md
- ✅ ARCHITECTURE.md
- ✅ DEVELOPMENT.md
- ✅ PROJECT_SUMMARY.md
- ✅ INDEX.md (本文件)

### 其他文件 (1 个)
- ✅ .gitignore

**总计**: 37 个文件

## 🎓 学习路径

### 初级用户
1. 阅读本 INDEX 文件了解结构
2. 阅读 [快速开始](QUICKSTART.md)
3. 运行 [example.py](example.py) 查看示例
4. 调用 API 进行数据提取

### 中级用户
1. 阅读 [完整文档](APP_README.md) 了解所有功能
2. 自定义 Prompt 以改进结果
3. 编写自己的测试用例
4. 集成到自己的应用

### 高级用户
1. 阅读 [架构设计](ARCHITECTURE.md) 理解设计决策
2. 阅读 [开发指南](DEVELOPMENT.md) 了解最佳实践
3. 实现新的 LLM 提供商
4. 优化性能和可扩展性
5. 贡献改进代码

## 🚀 下一步

- 🏃 快速开始: [QUICKSTART.md](QUICKSTART.md)
- 📖 完整文档: [APP_README.md](APP_README.md)
- 🏗️ 架构设计: [ARCHITECTURE.md](ARCHITECTURE.md)
- 🔧 开发指南: [DEVELOPMENT.md](DEVELOPMENT.md)

---

**最后更新**: 2024 年 10 月 24 日
**版本**: 1.0.0
**项目状态**: ✅ 完成
