"""
快速示例脚本 - 演示如何使用API
"""
import requests
import json
from typing import Dict, List, Any


def extract_from_raw_text(
    text: str,
    schema: List[Dict[str, Any]],
    api_url: str = "http://localhost:8000",
    model: str = "gpt-4-turbo-preview",
) -> Dict[str, Any]:
    """
    从原始文本提取数据
    
    Args:
        text: 原始文本
        schema: 数据schema
        api_url: API地址
        model: 使用的模型
        
    Returns:
        提取结果
    """
    endpoint = f"{api_url}/api/v1/extract"
    
    payload = {
        "source": "raw",
        "file": text,
        "schema": schema,
        "model": model,
    }
    
    print(f"\n📤 发送请求到: {endpoint}")
    print(f"📋 Schema: {json.dumps(schema, indent=2, ensure_ascii=False)}")
    print(f"📝 文本: {text[:100]}...")
    
    response = requests.post(endpoint, json=payload)
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ 成功！")
        print(f"📊 提取结果:")
        print(json.dumps(result["data"], indent=2, ensure_ascii=False))
        return result
    else:
        print(f"\n❌ 失败！状态码: {response.status_code}")
        print(f"📄 错误: {response.text}")
        return None


def extract_from_minio(
    url: str,
    schema: List[Dict[str, Any]],
    api_url: str = "http://localhost:8000",
    model: str = "gpt-4-turbo-preview",
) -> Dict[str, Any]:
    """
    从MinIO提取数据
    
    Args:
        url: MinIO文件URL
        schema: 数据schema
        api_url: API地址
        model: 使用的模型
        
    Returns:
        提取结果
    """
    endpoint = f"{api_url}/api/v1/extract"
    
    payload = {
        "source": "minio",
        "file": url,
        "schema": schema,
        "model": model,
    }
    
    print(f"\n📤 发送请求到: {endpoint}")
    print(f"📋 Schema: {json.dumps(schema, indent=2, ensure_ascii=False)}")
    print(f"📁 MinIO URL: {url}")
    
    response = requests.post(endpoint, json=payload)
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ 成功！")
        print(f"📊 提取结果:")
        print(json.dumps(result["data"], indent=2, ensure_ascii=False))
        return result
    else:
        print(f"\n❌ 失败！状态码: {response.status_code}")
        print(f"📄 错误: {response.text}")
        return None


def health_check(api_url: str = "http://localhost:8000") -> bool:
    """
    检查API健康状态
    
    Args:
        api_url: API地址
        
    Returns:
        是否健康
    """
    try:
        response = requests.get(f"{api_url}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API 健康检查通过")
            print(f"   服务: {data.get('service')}")
            print(f"   版本: {data.get('version')}")
            return True
        else:
            print(f"❌ API 不健康，状态码: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ 无法连接到 API: {api_url}")
        return False
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("🚀 LLM Document Parser 快速示例")
    print("=" * 60)
    
    # 1. 健康检查
    print("\n【步骤 1】检查API健康状态...")
    if not health_check():
        print("\n⚠️  请先启动API服务！")
        print("运行: python run.py")
        exit(1)
    
    # 2. 示例1: 从原始文本提取个人信息
    print("\n" + "=" * 60)
    print("【示例 1】从原始文本提取个人信息")
    print("=" * 60)
    
    text_example = """
    我叫李明，今年35岁，是一名资深的数据工程师。
    我住在北京，电话号码是13800138000，邮箱是liming@example.com。
    我在2020年12月20日加入了这家公司，基本工资是15000元。
    """
    
    person_schema = [
        {
            "name": "姓名",
            "field": "name",
            "type": "text",
            "required": True,
        },
        {
            "name": "年龄",
            "field": "age",
            "type": "int",
            "required": True,
        },
        {
            "name": "职位",
            "field": "position",
            "type": "text",
            "required": True,
        },
        {
            "name": "城市",
            "field": "city",
            "type": "text",
            "required": True,
        },
        {
            "name": "电话",
            "field": "phone",
            "type": "text",
            "required": False,
        },
        {
            "name": "邮箱",
            "field": "email",
            "type": "text",
            "required": False,
        },
        {
            "name": "入职日期",
            "field": "join_date",
            "type": "date",
            "required": False,
        },
        {
            "name": "月薪",
            "field": "salary",
            "type": "int",
            "required": False,
        },
    ]
    
    extract_from_raw_text(text_example, person_schema)
    
    # 3. 示例2: 从原始文本提取订单信息
    print("\n" + "=" * 60)
    print("【示例 2】从原始文本提取订单信息")
    print("=" * 60)
    
    order_text = """
    订单编号：PO-2024-001234
    客户名称：中国科学院
    订单日期：2024年1月15日
    订单金额：¥150,000.00
    订单状态：已支付
    预期交付日期：2024年2月28日
    """
    
    order_schema = [
        {
            "name": "订单编号",
            "field": "order_id",
            "type": "text",
            "required": True,
        },
        {
            "name": "客户名称",
            "field": "customer",
            "type": "text",
            "required": True,
        },
        {
            "name": "订单日期",
            "field": "order_date",
            "type": "date",
            "required": True,
        },
        {
            "name": "金额",
            "field": "amount",
            "type": "float",
            "required": True,
        },
        {
            "name": "支付状态",
            "field": "paid",
            "type": "boolean",
            "required": True,
        },
        {
            "name": "预期交付日期",
            "field": "delivery_date",
            "type": "date",
            "required": False,
        },
    ]
    
    extract_from_raw_text(order_text, order_schema)
    
    # 4. 示例3: MinIO文件提取（注释，需要实际的MinIO URL）
    print("\n" + "=" * 60)
    print("【示例 3】从MinIO提取（演示代码，需要实际URL）")
    print("=" * 60)
    
    print("\n示例代码:")
    print("""
    # 从MinIO的PDF文件提取简历信息
    resume_schema = [
        {"name": "姓名", "field": "name", "type": "text", "required": True},
        {"name": "邮箱", "field": "email", "type": "text", "required": True},
        {"name": "电话", "field": "phone", "type": "text", "required": False},
        {"name": "工作经验", "field": "experience", "type": "text", "required": False},
        {"name": "学位", "field": "education", "type": "text", "required": False},
    ]
    
    # 需要替换为实际的MinIO URL
    minio_url = "http://localhost:9000/documents/resume.pdf"
    extract_from_minio(minio_url, resume_schema)
    """)
    
    print("\n" + "=" * 60)
    print("✨ 示例完成！")
    print("=" * 60)
    print("\n📖 更多信息，请查看:")
    print("  - API文档: http://localhost:8000/docs")
    print("  - 完整README: APP_README.md")
    print("  - 开发指南: DEVELOPMENT.md")
