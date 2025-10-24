# 📇 快速参考卡 - LLM Document Parser

## 🎯 5分钟快速上手

### 1️⃣ 安装 (2分钟)
```bash
cd llm-doc-parser
pip install -r requirements.txt
```

### 2️⃣ 配置 (1分钟)
```bash
cp .env.example .env
# 编辑 .env 文件，填入 OPENAI_API_KEY
```

### 3️⃣ 启动 (1分钟)
```bash
python run.py
```

### 4️⃣ 测试 (1分钟)
访问: http://localhost:8000/docs

---

## 🔗 常用链接

| 地址 | 说明 |
|------|------|
| http://localhost:8000/docs | Swagger API 文档 |
| http://localhost:8000/health | 健康检查 |
| http://localhost:8000/api/v1/extract | 提取 API |

---

## 💻 常用命令

```bash
# 启动应用
python run.py

# 运行测试
pytest tests/ -v

# 查看示例
python example.py

# 验证项目
python verify_project.py

# Docker 启动
docker-compose up -d

# 停止 Docker
docker-compose down
```

---

## 📝 API 快速使用

### 原始文本提取
```bash
curl -X POST "http://localhost:8000/api/v1/extract" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "raw",
    "file": "张三，35岁，工程师",
    "schema": [
      {"name": "姓名", "field": "name", "type": "text", "required": true},
      {"name": "年龄", "field": "age", "type": "int", "required": true}
    ]
  }'
```

### MinIO 文件提取
```bash
curl -X POST "http://localhost:8000/api/v1/extract" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "minio",
    "file": "http://localhost:9000/bucket/file.pdf",
    "schema": [...]
  }'
```

---

## 🐍 Python 客户端

```python
import requests

url = "http://localhost:8000/api/v1/extract"
payload = {
    "source": "raw",
    "file": "文本内容",
    "schema": [
        {"name": "姓名", "field": "name", "type": "text", "required": true}
    ]
}

response = requests.post(url, json=payload)
print(response.json())
```

---

## 📂 关键文件

| 文件 | 说明 |
|------|------|
| app/main.py | 应用入口 |
| app/api/routes.py | API 路由 |
| app/llm/factory.py | LLM 工厂 |
| app/services/extract_service.py | 主服务 |
| .env.example | 环境配置 |
| requirements.txt | 依赖 |

---

## ⚙️ 配置参数

### .env 配置
```env
OPENAI_API_KEY=sk-xxx              # OpenAI 密钥（必需）
OPENAI_BASE_URL=                   # 基础 URL（可选）
MINIO_ENDPOINT=localhost:9000      # MinIO 地址
MINIO_ACCESS_KEY=minioadmin        # MinIO 访问密钥
MINIO_SECRET_KEY=minioadmin        # MinIO 秘钥
MINIO_SECURE=false                 # 是否 HTTPS
DEBUG=false                         # 调试模式
```

---

## 🚀 字段类型说明

| 类型 | 说明 | 示例 |
|------|------|------|
| text | 文本 | "张三" |
| int | 整数 | 25 |
| float | 浮点 | 3.14 |
| boolean | 布尔 | true |
| date | 日期 | "2024-01-01" |
| datetime | 日期时间 | "2024-01-01 12:00:00" |

---

## 📚 文档位置

```
QUICKSTART.md        ← 从这里开始！
APP_README.md        ← 完整功能
ARCHITECTURE.md      ← 系统设计
DEVELOPMENT.md       ← 开发指南
PROJECT_SUMMARY.md   ← 项目总结
INDEX.md             ← 资源导航
```

---

## 🐛 常见问题速答

**Q: 无法导入 app？**
A: 确保在项目根目录执行，且安装了依赖

**Q: OpenAI API 超时？**
A: 检查网络和 API 密钥有效性

**Q: MinIO 连接失败？**
A: 确认 MinIO 服务运行，检查端点配置

**Q: 提取结果不准确？**
A: 优化 Schema 描述或使用更好的模型

---

## 🏗️ 项目结构速览

```
app/
├── api/              # 路由
├── core/             # 配置、异常
├── models/           # 数据模型
├── llm/              # LLM 实现（工厂模式）
├── services/         # 业务逻辑
└── main.py           # 应用入口
```

---

## ✨ 核心特性

- ✅ MinIO + 原始文本
- ✅ 多格式文件处理
- ✅ OpenAI LLM
- ✅ 优化 Prompt
- ✅ 工厂模式（可扩展）
- ✅ 异步处理
- ✅ Docker 支持

---

## 🔒 安全提示

⚠️ **不要**:
- 在代码中硬编码 API 密钥
- 提交 .env 文件到版本控制
- 在生产环境开启 DEBUG 模式

✅ **应该**:
- 使用环境变量存储密钥
- 定期轮换 API 密钥
- 启用 HTTPS
- 监控 API 使用

---

## 📊 性能建议

- 使用异步调用充分利用性能
- 考虑添加缓存减少重复调用
- 大文件分块处理
- 优化 Prompt 减少失败

---

## 🎓 学习路径

### 5分钟学会
1. QUICKSTART.md
2. 运行 example.py
3. 用 Swagger 测试

### 30分钟理解
1. APP_README.md
2. 查看代码示例
3. 自定义 Schema

### 2小时精通
1. ARCHITECTURE.md
2. DEVELOPMENT.md
3. 实现自定义 LLM

---

## 🔄 工作流程

```
用户请求
  ↓
API 验证
  ↓
获取文件
  ↓
提取文本
  ↓
构建 Prompt
  ↓
调用 OpenAI
  ↓
解析响应
  ↓
类型转换
  ↓
返回 JSON
```

---

## 📞 获取帮助

### 快速检查
```bash
python verify_project.py  # 验证环境
python example.py         # 查看示例
pytest tests/ -v          # 运行测试
```

### 查看文档
- [QUICKSTART.md](QUICKSTART.md) - 快速开始
- [APP_README.md](APP_README.md) - 完整文档
- [ARCHITECTURE.md](ARCHITECTURE.md) - 架构设计

### 访问 API 文档
http://localhost:8000/docs

---

## 🎉 快速检查清单

- [ ] 安装依赖: `pip install -r requirements.txt`
- [ ] 配置环境: `cp .env.example .env` 并编辑
- [ ] 启动应用: `python run.py`
- [ ] 访问 API: http://localhost:8000/docs
- [ ] 运行示例: `python example.py`
- [ ] 验证项目: `python verify_project.py`

---

## 🚀 下一步行动

1. **立即开始**: `python run.py`
2. **查看文档**: [QUICKSTART.md](QUICKSTART.md)
3. **测试 API**: http://localhost:8000/docs
4. **运行示例**: `python example.py`
5. **深入学习**: [ARCHITECTURE.md](ARCHITECTURE.md)

---

**版本**: 1.0.0 | **状态**: ✅ 生产就绪 | **日期**: 2024年10月24日
