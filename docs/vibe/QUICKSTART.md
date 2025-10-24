# 快速使用指南 (中文)

## 🚀 5分钟快速开始

### 1️⃣ 环境准备

```bash
# 克隆项目
cd llm-doc-parser

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境 (Windows)
venv\Scripts\activate

# 激活虚拟环境 (Linux/Mac)
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2️⃣ 配置环境变量

复制示例文件:
```bash
cp .env.example .env
```

编辑 `.env` 文件，填入您的 OpenAI API 密钥:

```env
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxx
```

### 3️⃣ 启动应用

```bash
python run.py
```

应用将在 `http://localhost:8000` 启动

## 📖 API 使用示例

### 示例 1: 提取个人信息

**请求**:
```bash
curl -X POST "http://localhost:8000/api/v1/extract" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "raw",
    "file": "张三，35岁，是一名高级工程师，住在北京。",
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
      },
      {
        "name": "城市",
        "field": "city",
        "type": "text",
        "required": false
      }
    ]
  }'
```

**响应**:
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
    },
    {
      "field": "city",
      "type": "text",
      "value": "北京"
    }
  ],
  "code": "200",
  "message": "Success"
}
```

### 示例 2: 提取订单信息

**请求**:
```bash
curl -X POST "http://localhost:8000/api/v1/extract" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "raw",
    "file": "订单号PO-2024-001，客户是中国科学院，订单日期2024年1月15日，总额¥150000，已支付，预计2024年2月28日交付。",
    "schema": [
      {
        "name": "订单编号",
        "field": "order_id",
        "type": "text",
        "required": true
      },
      {
        "name": "客户名称",
        "field": "customer",
        "type": "text",
        "required": true
      },
      {
        "name": "订单日期",
        "field": "order_date",
        "type": "date",
        "required": true
      },
      {
        "name": "订单金额",
        "field": "amount",
        "type": "float",
        "required": true
      },
      {
        "name": "是否支付",
        "field": "is_paid",
        "type": "boolean",
        "required": true
      },
      {
        "name": "预期交付日期",
        "field": "delivery_date",
        "type": "date",
        "required": false
      }
    ]
  }'
```

### 示例 3: 提取表格数据

**请求**:
```bash
curl -X POST "http://localhost:8000/api/v1/extract" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "raw",
    "file": "员工编号001，李明，销售部，年薪50万，入职日期2020年1月15日。",
    "schema": [
      {
        "name": "员工编号",
        "field": "employee_id",
        "type": "text",
        "required": true
      },
      {
        "name": "员工名字",
        "field": "name",
        "type": "text",
        "required": true
      },
      {
        "name": "部门",
        "field": "department",
        "type": "text",
        "required": true
      },
      {
        "name": "年薪(万元)",
        "field": "salary",
        "type": "float",
        "required": false
      },
      {
        "name": "入职日期",
        "field": "hire_date",
        "type": "date",
        "required": false
      }
    ]
  }'
```

## 🐍 Python 客户端示例

### 使用 requests 库

```python
import requests
import json

def extract_data(text, schema):
    """提取数据"""
    url = "http://localhost:8000/api/v1/extract"
    
    payload = {
        "source": "raw",
        "file": text,
        "schema": schema,
        "model": "gpt-4-turbo-preview"
    }
    
    response = requests.post(url, json=payload)
    return response.json()

# 使用示例
text = "张三，35岁，工程师"

schema = [
    {
        "name": "姓名",
        "field": "name",
        "type": "text",
        "required": True
    },
    {
        "name": "年龄",
        "field": "age",
        "type": "int",
        "required": True
    },
    {
        "name": "职位",
        "field": "position",
        "type": "text",
        "required": False
    }
]

result = extract_data(text, schema)
print(json.dumps(result, indent=2, ensure_ascii=False))
```

### 使用 httpx 库 (异步)

```python
import httpx
import json
import asyncio

async def extract_data_async(text, schema):
    """异步提取数据"""
    url = "http://localhost:8000/api/v1/extract"
    
    payload = {
        "source": "raw",
        "file": text,
        "schema": schema,
        "model": "gpt-4-turbo-preview"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload)
        return response.json()

# 使用示例
async def main():
    text = "张三，35岁，工程师"
    schema = [...]
    
    result = await extract_data_async(text, schema)
    print(json.dumps(result, indent=2, ensure_ascii=False))

asyncio.run(main())
```

## 📁 从 MinIO 提取文件

### 准备 MinIO

```bash
# 使用 Docker Compose 启动 MinIO
docker-compose up -d minio

# 或者手动启动
docker run -p 9000:9000 -p 9001:9001 \
  -e MINIO_ROOT_USER=minioadmin \
  -e MINIO_ROOT_PASSWORD=minioadmin \
  minio/minio server /data
```

访问 MinIO 控制台: `http://localhost:9001`
- 用户名: `minioadmin`
- 密码: `minioadmin`

### 上传文件到 MinIO

使用 MinIO 客户端:

```bash
# 安装 mc (MinIO Client)
# 参考: https://min.io/docs/minio/linux/reference/minio-mc.html

# 配置连接
mc alias set myminio http://localhost:9000 minioadmin minioadmin

# 创建 bucket
mc mb myminio/documents

# 上传文件
mc cp resume.pdf myminio/documents/
```

### 从 MinIO 提取

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
        "required": false
      },
      {
        "name": "邮箱",
        "field": "email",
        "type": "text",
        "required": false
      }
    ]
  }'
```

## 🐳 Docker 部署

### 使用 Docker Compose

```bash
# 启动应用 (包含 MinIO)
docker-compose up -d

# 查看日志
docker-compose logs -f llm-parser

# 停止应用
docker-compose down
```

### 使用 Docker

```bash
# 构建镜像
docker build -t llm-doc-parser .

# 运行容器
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=sk-xxxxxxx \
  -e MINIO_ENDPOINT=host.docker.internal:9000 \
  llm-doc-parser
```

## 📊 API 文档

启动应用后访问:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🧪 运行测试

```bash
# 安装测试依赖
pip install pytest pytest-asyncio httpx

# 运行所有测试
pytest tests/

# 运行特定测试
pytest tests/test_api.py::test_health_check -v

# 生成覆盖率报告
pytest tests/ --cov=app --cov-report=html

# 运行测试示例脚本
python example.py
```

## 🔧 常见问题

### Q1: 如何设置代理访问 OpenAI?

编辑 `.env`:
```env
OPENAI_BASE_URL=https://api.openai.com/v1
```

或者使用第三方代理:
```env
OPENAI_BASE_URL=https://your-proxy-url/v1
```

### Q2: 如何处理超大文件?

对于大文件 (>50MB):
1. 分块上传到 MinIO
2. 或者将内容分块后多次调用 API

### Q3: 如何提高提取准确度?

1. 优化 schema 描述 - 使用更详细的字段说明
2. 选择更好的模型 - 使用 `gpt-4-turbo-preview` 或更高版本
3. 提供上下文 - 在文本中包含更多相关信息
4. 调整 temperature - 对于提取任务，使用较低的 temperature (0.1)

### Q4: 支持哪些文件格式?

通过 Unstructured 库支持:
- PDF (.pdf)
- Word (.docx, .doc)
- Excel (.xlsx, .xls)
- PowerPoint (.pptx, .ppt)
- 纯文本 (.txt)
- HTML (.html)
- Markdown (.md)

### Q5: 如何监控应用性能?

1. 查看日志: `docker-compose logs -f llm-parser`
2. 访问健康检查: `curl http://localhost:8000/health`
3. 考虑集成 Prometheus 和 Grafana

## 📞 获取帮助

- 查看完整文档: `APP_README.md`
- 查看架构设计: `ARCHITECTURE.md`
- 查看开发指南: `DEVELOPMENT.md`
- API 交互式文档: http://localhost:8000/docs

## ⚡ 性能建议

1. **使用异步调用**: 充分利用应用的异步特性
2. **批量处理**: 如果可能，合并多个提取请求
3. **缓存结果**: 对于相同的输入，考虑缓存结果
4. **优化 Prompt**: 更清晰的 Prompt 能减少调用失败
5. **监控成本**: 跟踪 OpenAI API 的使用成本

## 🔐 安全建议

1. ✅ 不要在代码中硬编码 API 密钥，使用环境变量
2. ✅ 生产环境使用 HTTPS
3. ✅ 限制 API 访问 (添加认证/授权)
4. ✅ 定期轮换 API 密钥
5. ✅ 监控 API 使用情况，检测异常行为

## 📈 下一步

- 集成到您的应用
- 自定义 Prompt 以获得更好的结果
- 添加数据库持久化
- 实现缓存机制
- 添加异步任务队列 (Celery)
