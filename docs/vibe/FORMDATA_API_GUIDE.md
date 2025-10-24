# FormData API 使用指南

本指南展示如何使用 FormData 格式调用提取 API。

## API 端点

```
POST /extract
```

## 请求格式

使用 `application/x-www-form-urlencoded` 或 `multipart/form-data` 格式。

### 参数说明

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `source` | string | ✓ | 文件来源: `minio` 或 `raw` |
| `file` | string | * | MinIO URL 或原始文本内容（source=minio 时必需） |
| `upload_file` | file | * | 上传的文件（可替代 file 参数） |
| `schema` | string | ✓ | JSON 格式的 Schema 字段定义数组 |
| `provider` | string | | LLM 提供商: `openai`\|`azure`\|`claude`\|`gemini`\|`custom`（默认: openai） |
| `model` | string | | LLM 模型名称（可选，不指定使用提供商默认值） |

## cURL 示例

### 1. 基本使用（原始文本）

```bash
curl -X POST http://localhost:8000/extract \
  -F "source=raw" \
  -F "file=张三是一名程序员，出生于1990年5月15日" \
  -F 'schema=[
    {"name":"人名","field":"name","type":"text","required":true},
    {"name":"职业","field":"occupation","type":"text","required":true},
    {"name":"出生日期","field":"birth_date","type":"date","required":true}
  ]' \
  -F "provider=openai" \
  -F "model=gpt-4o-mini"
```

### 2. 使用文件上传

```bash
# 上传 PDF 文件
curl -X POST http://localhost:8000/extract \
  -F "source=raw" \
  -F "upload_file=@document.pdf" \
  -F 'schema=[
    {"name":"标题","field":"title","type":"text"},
    {"name":"内容","field":"content","type":"text"}
  ]' \
  -F "provider=openai"

# 上传文本文件
curl -X POST http://localhost:8000/extract \
  -F "source=raw" \
  -F "upload_file=@data.txt" \
  -F 'schema=[
    {"name":"数据","field":"data","type":"text"}
  ]'
```

### 3. 使用 Claude 提供商

```bash
curl -X POST http://localhost:8000/extract \
  -F "source=raw" \
  -F "file=张三是一名软件工程师" \
  -F 'schema=[
    {"name":"职位","field":"position","type":"text"}
  ]' \
  -F "provider=claude" \
  -F "model=claude-3-sonnet-20240229"
```

### 4. 使用 Custom 提供商

```bash
# 首先设置环境变量
export CUSTOM_BASE_URL=https://chat.ecnu.edu.cn/open/api/v1
export CUSTOM_API_KEY=sk-xxxxxxxxxxxx

# 然后发送请求（无需在请求中传递 custom_base_url 和 custom_api_key）
curl -X POST http://localhost:8000/extract \
  -F "source=raw" \
  -F "file=华为是中国领先的电信设备制造商" \
  -F 'schema=[
    {"name":"公司","field":"company","type":"text"}
  ]' \
  -F "provider=custom"
```

### 5. 使用 Gemini 提供商

```bash
curl -X POST http://localhost:8000/extract \
  -F "source=raw" \
  -F "file=李四是产品经理" \
  -F 'schema=[
    {"name":"职位","field":"position","type":"text"}
  ]' \
  -F "provider=gemini" \
  -F "model=gemini-2.0-flash"
```

### 6. 复杂 Schema 示例

```bash
curl -X POST http://localhost:8000/extract \
  -F "source=raw" \
  -F "file=李五，28岁，是一名从事AI研究的科学家。他的月薪是25000元，拥有3项专利，已发表10篇论文。" \
  -F 'schema=[
    {"name":"姓名","field":"name","type":"text","required":true},
    {"name":"年龄","field":"age","type":"int","required":true},
    {"name":"职业","field":"occupation","type":"text","required":true},
    {"name":"月薪","field":"monthly_salary","type":"int","required":false},
    {"name":"专利数","field":"patent_count","type":"int","required":false},
    {"name":"论文数","field":"paper_count","type":"int","required":false}
  ]' \
  -F "provider=openai"
```

## Python 示例

### 使用 requests 库

```python
import requests
import json

schema = [
    {"name":"姓名","field":"name","type":"text","required":True},
    {"name":"年龄","field":"age","type":"int","required":True}
]

files = {
    'source': (None, 'raw'),
    'file': (None, '张三，32岁'),
    'schema': (None, json.dumps(schema, ensure_ascii=False)),
    'provider': (None, 'openai'),
}

response = requests.post(
    'http://localhost:8000/extract',
    files=files,
    timeout=60
)

print(response.json())
```

### 使用 aiohttp 库（异步）

```python
import aiohttp
import json

async def extract():
    schema = [
        {"name":"姓名","field":"name","type":"text","required":True},
        {"name":"年龄","field":"age","type":"int","required":True}
    ]
    
    data = aiohttp.FormData()
    data.add_field('source', 'raw')
    data.add_field('file', '张三，32岁')
    data.add_field('schema', json.dumps(schema, ensure_ascii=False))
    data.add_field('provider', 'openai')
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            'http://localhost:8000/extract',
            data=data
        ) as resp:
            return await resp.json()
```

### 文件上传

```python
import requests
import json

schema = [
    {"name":"标题","field":"title","type":"text"}
]

with open('document.txt', 'rb') as f:
    files = {
        'source': (None, 'raw'),
        'upload_file': f,
        'schema': (None, json.dumps(schema, ensure_ascii=False)),
    }
    
    response = requests.post(
        'http://localhost:8000/extract',
        files=files
    )

print(response.json())
```

## JavaScript/TypeScript 示例

### 使用 fetch API

```javascript
const schema = [
  {name:"姓名", field:"name", type:"text", required:true},
  {name:"年龄", field:"age", type:"int", required:true}
];

const formData = new FormData();
formData.append('source', 'raw');
formData.append('file', '张三，32岁');
formData.append('schema', JSON.stringify(schema));
formData.append('provider', 'openai');

const response = await fetch('http://localhost:8000/extract', {
  method: 'POST',
  body: formData
});

const result = await response.json();
console.log(result);
```

### 文件上传

```javascript
const schema = [
  {name:"标题", field:"title", type:"text"}
];

const fileInput = document.querySelector('input[type="file"]');
const formData = new FormData();

formData.append('source', 'raw');
formData.append('upload_file', fileInput.files[0]);
formData.append('schema', JSON.stringify(schema));

const response = await fetch('http://localhost:8000/extract', {
  method: 'POST',
  body: formData
});

const result = await response.json();
```

## Schema 定义

### Schema 字段格式

```json
{
  "name": "字段显示名称",
  "field": "字段标识符",
  "type": "字段类型",
  "required": true/false
}
```

### 支持的字段类型

| 类型 | 说明 | 示例 |
|------|------|------|
| `text` | 文本 | "张三" |
| `int` | 整数 | 32 |
| `float` | 浮点数 | 123.45 |
| `boolean` | 布尔值 | true/false |
| `date` | 日期 | "2024-01-01" |
| `datetime` | 日期时间 | "2024-01-01 12:00:00" |

## 响应格式

### 成功响应

```json
{
  "code": "200",
  "message": "Success",
  "data": [
    {
      "field": "name",
      "type": "text",
      "value": "张三"
    },
    {
      "field": "age",
      "type": "int",
      "value": 32
    }
  ]
}
```

### 错误响应

```json
{
  "code": "INVALID_SCHEMA",
  "message": "Schema JSON 格式无效"
}
```

### 错误代码

| 错误代码 | 说明 |
|----------|------|
| `INVALID_INPUT` | 输入参数无效 |
| `INVALID_SCHEMA` | Schema 格式错误 |
| `INTERNAL_ERROR` | 服务器内部错误 |
| 其他 | LLM 相关错误 |

## 最佳实践

1. **Schema 验证**：在发送请求前验证 JSON Schema 的有效性
2. **超时设置**：为长时间运行的请求设置合理的超时时间（推荐 60 秒）
3. **错误处理**：始终检查响应状态码和错误消息
4. **文件大小**：上传文件大小限制为 100MB
5. **提供商选择**：
   - 通用任务：使用 `openai`（默认）
   - 成本敏感：使用 `gemini`（最便宜）
   - 复杂推理：使用 `claude`（最强的推理）
   - 本地 API：使用 `custom`（自定义端点）

## 环境变量配置

### Custom 提供商环境变量

当使用 `provider=custom` 时，需要配置以下环境变量：

```bash
# 必需：自定义 API 基础 URL（OpenAI 兼容的 API 服务）
CUSTOM_BASE_URL=https://your-api-endpoint.com/v1

# 可选：自定义 API 密钥
CUSTOM_API_KEY=sk-your-api-key-here
```

### 配置方法

#### 方法 1：在 `.env` 文件中配置

编辑项目根目录的 `.env` 文件：

```env
# Custom 提供商配置
CUSTOM_BASE_URL=https://chat.ecnu.edu.cn/open/api/v1
CUSTOM_API_KEY=sk-xxxxxxxxxxxx
```

#### 方法 2：命令行设置（Linux/macOS）

```bash
export CUSTOM_BASE_URL=https://your-api-endpoint.com/v1
export CUSTOM_API_KEY=sk-your-api-key-here
python -m uvicorn app.main:app --reload
```

#### 方法 3：命令行设置（Windows PowerShell）

```powershell
$env:CUSTOM_BASE_URL="https://your-api-endpoint.com/v1"
$env:CUSTOM_API_KEY="sk-your-api-key-here"
python -m uvicorn app.main:app --reload
```

### 其他 LLM 提供商环境变量

| 提供商 | 环境变量 | 说明 |
|--------|----------|------|
| `openai` | `OPENAI_API_KEY` | OpenAI API 密钥 |
| `azure` | `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT` | Azure OpenAI 密钥和端点 |
| `claude` | `ANTHROPIC_API_KEY` | Anthropic API 密钥 |
| `gemini` | `GOOGLE_API_KEY` | Google Gemini API 密钥 |
| `custom` | `CUSTOM_BASE_URL`, `CUSTOM_API_KEY` | 自定义 API 端点和密钥 |

### 验证环境变量

使用以下 Python 脚本验证环境变量是否正确设置：

```python
import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# 检查 Custom 提供商环境变量
print("CUSTOM_BASE_URL:", os.getenv("CUSTOM_BASE_URL"))
print("CUSTOM_API_KEY:", os.getenv("CUSTOM_API_KEY"))

# 其他提供商
print("OPENAI_API_KEY:", "✓" if os.getenv("OPENAI_API_KEY") else "✗")
print("AZURE_OPENAI_API_KEY:", "✓" if os.getenv("AZURE_OPENAI_API_KEY") else "✗")
print("ANTHROPIC_API_KEY:", "✓" if os.getenv("ANTHROPIC_API_KEY") else "✗")
print("GOOGLE_API_KEY:", "✓" if os.getenv("GOOGLE_API_KEY") else "✗")
```

## 故障排查

### 问题：Schema JSON 格式错误

**解决**：确保 JSON 格式正确，所有字符串使用双引号：
```bash
# ✗ 错误
-F 'schema=[{name:"name"}]'

# ✓ 正确
-F 'schema=[{"name":"name"}]'
```

### 问题：文件编码错误

**解决**：确保上传的文件使用 UTF-8 编码

### 问题：超时

**解决**：
1. 增加超时时间
2. 检查网络连接
3. 尝试使用更快的模型（如 `gemini-2.0-flash`）

### 问题：Custom 提供商错误 - "CUSTOM_BASE_URL 未设置"

**错误消息**：
```
使用 custom 提供商时必须设置环境变量 CUSTOM_BASE_URL
```

**解决**：
1. 确保在 `.env` 文件中设置了 `CUSTOM_BASE_URL`
2. 重启应用以加载新的环境变量
3. 验证环境变量已正确设置：
   ```bash
   echo $CUSTOM_BASE_URL  # Linux/macOS
   echo $env:CUSTOM_BASE_URL  # Windows PowerShell
   ```

### 问题：Custom 提供商连接失败

**错误消息**：
```
ConnectionError: Failed to connect to custom API endpoint
```

**解决**：
1. 检查 `CUSTOM_BASE_URL` 是否正确
2. 检查网络连接和防火墙设置
3. 确认远程 API 服务是否在线
4. 如果使用 HTTPS，检查 SSL 证书是否有效

### 问题：Custom 提供商认证失败

**错误消息**：
```
AuthenticationError: Invalid API key
```

**解决**：
1. 检查 `CUSTOM_API_KEY` 是否正确
2. 检查 API 密钥是否过期或已被撤销
3. 确保 API 密钥有适当的权限

## 更多信息

- 查看 `examples/example_formdata_api.py` 了解完整示例
- 查看 `docs/MULTI_PROVIDER_GUIDE.md` 了解提供商配置
- 查看 `docs/API.md` 了解 API 文档
