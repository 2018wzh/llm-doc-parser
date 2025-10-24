# 开发指南

## 项目设置

### 1. 虚拟环境

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境 (Windows)
venv\Scripts\activate

# 激活虚拟环境 (Linux/Mac)
source venv/bin/activate
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 开发依赖

```bash
pip install pytest pytest-asyncio pytest-cov black flake8 mypy
```

## 开发工作流

### 代码风格

使用 Black 进行代码格式化：

```bash
black app/ tests/
```

使用 flake8 进行代码检查：

```bash
flake8 app/ tests/
```

### 类型检查

```bash
mypy app/
```

### 测试

```bash
# 运行所有测试
pytest tests/

# 运行特定文件的测试
pytest tests/test_api.py

# 运行特定测试函数
pytest tests/test_api.py::test_health_check

# 显示详细信息
pytest tests/ -v

# 生成覆盖率报告
pytest tests/ --cov=app
```

## 项目约定

### 代码结构

1. **模块组织**
   - 相关功能放在同一个包中
   - 每个模块有明确的职责
   - 避免循环依赖

2. **命名规范**
   - 类名: PascalCase (如 `ExtractService`)
   - 函数/方法: snake_case (如 `extract_text`)
   - 常量: UPPER_SNAKE_CASE (如 `MAX_FILE_SIZE`)
   - 私有方法/属性: 前缀下划线 (如 `_parse_response`)

3. **文档**
   - 所有公开API都需要docstring
   - 使用Google风格的docstring
   - 包括参数、返回值和异常说明

### 示例 Docstring

```python
def extract(self, content: str, schema: List[SchemaField], model: str) -> List[ExtractedValue]:
    """
    根据schema和内容提取数据
    
    Args:
        content: 文件内容
        schema: 数据schema
        model: 模型名称
        
    Returns:
        提取的数据列表
        
    Raises:
        LLMException: 如果LLM调用失败
    """
    pass
```

## 扩展开发

### 添加新的 LLM 提供商

1. 在 `app/llm/` 下创建新文件 `your_llm.py`

```python
from app.llm.base import BaseLLM
from app.models import SchemaField, ExtractedValue

class YourLLM(BaseLLM):
    def __init__(self):
        # 初始化客户端
        pass
    
    async def extract(self, content: str, schema: List[SchemaField], model: str) -> List[ExtractedValue]:
        # 实现提取逻辑
        pass
    
    def _build_prompt(self, content: str, schema: List[SchemaField]) -> str:
        # 构建Prompt
        pass
    
    def _parse_response(self, response: str, schema: List[SchemaField]) -> List[ExtractedValue]:
        # 解析响应
        pass
```

2. 在 `app/llm/__init__.py` 中导入

```python
from .your_llm import YourLLM
```

3. 在 `app/llm/factory.py` 中注册

```python
_providers: Dict[str, Type[BaseLLM]] = {
    "openai": OpenAILLM,
    "your_provider": YourLLM,  # 添加这行
}
```

### 添加新的 API 端点

1. 在 `app/api/routes.py` 中添加路由

```python
@router.post("/api/v1/your-endpoint")
async def your_endpoint(request: YourRequest) -> YourResponse:
    """
    端点描述
    """
    # 实现逻辑
    pass
```

2. 在 `app/models/schemas.py` 中定义数据模型

```python
class YourRequest(BaseModel):
    field1: str
    field2: int

class YourResponse(BaseModel):
    result: str
```

## 调试

### 启用调试模式

编辑 `.env`:
```env
DEBUG=true
```

### 日志级别

编辑 `app/main.py`:
```python
logging.basicConfig(level=logging.DEBUG)
```

### 使用 IDE 调试器

#### VS Code

创建 `.vscode/launch.json`:
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "FastAPI",
            "type": "python",
            "request": "launch",
            "module": "uvicorn",
            "args": ["app.main:app", "--reload"],
            "jinja": true,
            "justMyCode": true
        }
    ]
}
```

#### PyCharm

1. 右键项目 → Run → Edit Configurations
2. 添加 Python 配置
3. Module: `uvicorn`
4. Parameters: `app.main:app --reload`

## 性能优化

### 1. 异步处理

使用 `async/await` 处理 I/O 操作：

```python
async def download_file(self, url: str) -> bytes:
    # 异步下载
    pass
```

### 2. 缓存

考虑使用缓存减少重复调用：

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_operation(param: str) -> str:
    pass
```

### 3. 批量操作

对大文本进行分块处理：

```python
def chunk_text(text: str, chunk_size: int = 1000) -> List[str]:
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
```

## 部署

### 生产环境配置

```bash
# 安装生产依赖
pip install gunicorn

# 使用Gunicorn运行
gunicorn -w 4 -b 0.0.0.0:8000 app.main:app
```

### Docker 部署

创建 `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

运行：
```bash
docker build -t llm-doc-parser .
docker run -p 8000:8000 --env-file .env llm-doc-parser
```

## 常见问题

### 1. 如何处理大文件？

- 使用流式处理
- 分块读取
- 考虑异步处理

### 2. 如何提高 LLM 准确度？

- 优化 Prompt
- 使用更好的模型
- 提供更清晰的 Schema
- 添加示例

### 3. 如何处理超时？

设置请求超时：

```python
from openai import AsyncOpenAI

client = AsyncOpenAI(
    api_key=settings.OPENAI_API_KEY,
    timeout=30.0,  # 30秒超时
)
```

## 参考资源

- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [Pydantic 文档](https://docs.pydantic.dev/)
- [OpenAI API](https://platform.openai.com/docs)
- [Unstructured 文档](https://unstructured.io/)
- [MinIO 文档](https://docs.min.io/)
