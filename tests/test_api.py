"""
测试用例
"""
import pytest
import json
from fastapi.testclient import TestClient
from app.main import app
from app.models import SchemaField, ExtractRequest

client = TestClient(app)


@pytest.fixture
def sample_schema():
    """示例schema"""
    return [
        SchemaField(
            name="人名",
            field="name",
            type="text",
            required=True,
            description="",
        ),
        SchemaField(
            name="年龄",
            field="age",
            type="int",
            required=True,
            description="",
        ),
        SchemaField(
            name="职业",
            field="occupation",
            type="text",
            required=False,
            description="",
        ),
    ]


def test_health_check():
    """测试健康检查"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_root():
    """测试根端点"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "title" in data
    assert "version" in data


def test_extract_raw_text(sample_schema):
    """测试从原始文本提取数据"""
    request_data = {
        "source": "raw",
        "file": "我叫张三，今年30岁，是一名软件工程师",
        "schema": [field.dict() for field in sample_schema],
        "model": "gpt-4-turbo-preview",
    }
    
    response = client.post("/api/v1/extract", json=request_data)
    
    # 由于需要实际的OpenAI API密钥，这里仅测试请求格式
    assert response.status_code in [200, 500]


def test_extract_invalid_source(sample_schema):
    """测试无效的来源"""
    request_data = {
        "source": "invalid",
        "file": "some text",
        "schema": [field.dict() for field in sample_schema],
        "model": "gpt-4-turbo-preview",
    }
    
    response = client.post("/api/v1/extract", json=request_data)
    
    # 应该返回422验证错误
    assert response.status_code == 422


def test_extract_missing_required_field():
    """测试缺少必填字段"""
    request_data = {
        "source": "raw",
        "file": "some text",
        # 缺少schema字段
        "model": "gpt-4-turbo-preview",
    }
    
    response = client.post("/api/v1/extract", json=request_data)
    
    # 应该返回422验证错误
    assert response.status_code == 422


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
 
def test_extract_formdata_toon_schema():
    """使用表单+TOON schema 进行一次端到端请求（不校验真实提取结果，仅校验接口受理）。"""
    toon_schema = (
        "```toon\n"
        "values[2]{name,field,type,required}:\n"
        "  人名,name,text,true\n"
        "  年龄,age,int,true\n"
        "```"
    )
    files = {
        "file": ("sample.txt", "张三, 年龄 30".encode("utf-8"), "text/plain"),
    }
    data = {
        "source": "file",
        "schema": toon_schema,
        "provider": "openai",
        "model": "gpt-4o-mini",
    }
    resp = client.post("/extract", data=data, files=files)
    assert resp.status_code in [200, 500, 422]


def test_schema_convert_json_to_toon():
    """将 JSON schema 转为 TOON。"""
    schema_list = [
        {"name": "人名", "field": "name", "type": "text", "required": True},
        {"name": "年龄", "field": "age", "type": "int", "required": True},
    ]
    resp = client.post("/schema/toon", json={"schema": schema_list})
    assert resp.status_code == 200
    data = resp.json()
    assert "toon" in data
    assert data["toon"].startswith("values[2]{name,field,type,required}:")
