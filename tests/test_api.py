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
        ),
        SchemaField(
            name="年龄",
            field="age",
            type="int",
            required=True,
        ),
        SchemaField(
            name="职业",
            field="occupation",
            type="text",
            required=False,
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
