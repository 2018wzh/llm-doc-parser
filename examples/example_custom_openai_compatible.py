"""
Custom (OpenAI 兼容) LLM 使用示例

演示如何使用 OpenAI 兼容的本地或远程服务：
- LM Studio
- Ollama  
- vLLM
- LocalAI
- 任何其他兼容 OpenAI API 的服务
"""
import asyncio
import httpx
from app.models import ExtractRequest, SchemaField
from app.services import ExtractService


async def main():
    """主函数"""
    
    # 创建提取服务
    extract_service = ExtractService()
    
    # =====================================================
    # 示例 1: 使用 LM Studio 本地服务
    # =====================================================
    print("=" * 60)
    print("示例 1: LM Studio (http://localhost:1234/v1)")
    print("=" * 60)
    
    request_lm_studio = ExtractRequest(
        source="raw",
        file="张三是一名Python开发工程师，出生于1990年5月15日，工作经验5年。",
        schema=[
            SchemaField(
                name="姓名",
                field="name",
                type="text",
                required=True,
            ),
            SchemaField(
                name="职位",
                field="position",
                type="text",
                required=True,
            ),
            SchemaField(
                name="出生日期",
                field="birth_date",
                type="date",
                required=True,
            ),
            SchemaField(
                name="工作年限",
                field="work_experience",
                type="int",
                required=True,
            ),
        ],
        provider="custom",
        model="neural-chat",  # LM Studio 中的模型名称
        custom_base_url="http://localhost:1234/v1",
        custom_api_key="not-needed",
    )
    
    try:
        print("\n请求内容:")
        print(f"文本: {request_lm_studio.file}")
        print(f"提供商: {request_lm_studio.provider}")
        print(f"模型: {request_lm_studio.model}")
        print(f"API基础URL: {request_lm_studio.custom_base_url}")
        
        result = await extract_service.extract(request_lm_studio)
        
        print("\n提取结果:")
        for item in result:
            print(f"  {item.field} ({item.type}): {item.value}")
            
    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")
        print("提示: 请确保 LM Studio 服务正在运行 (http://localhost:1234)")
    
    # =====================================================
    # 示例 2: 使用 Ollama 本地服务
    # =====================================================
    print("\n" + "=" * 60)
    print("示例 2: Ollama (http://localhost:11434/v1)")
    print("=" * 60)
    
    request_ollama = ExtractRequest(
        source="raw",
        file="李四是一名数据科学家，月薪15000元，精通 Python 和 R 语言。",
        schema=[
            SchemaField(
                name="姓名",
                field="name",
                type="text",
                required=True,
            ),
            SchemaField(
                name="职位",
                field="position",
                type="text",
                required=True,
            ),
            SchemaField(
                name="月薪",
                field="salary",
                type="int",
                required=True,
            ),
            SchemaField(
                name="技能",
                field="skills",
                type="text",
                required=True,
            ),
        ],
        provider="custom",
        model="llama2",  # Ollama 中的模型名称
        custom_base_url="http://localhost:11434/v1",
        custom_api_key="not-needed",
    )
    
    try:
        print("\n请求内容:")
        print(f"文本: {request_ollama.file}")
        print(f"提供商: {request_ollama.provider}")
        print(f"模型: {request_ollama.model}")
        print(f"API基础URL: {request_ollama.custom_base_url}")
        
        result = await extract_service.extract(request_ollama)
        
        print("\n提取结果:")
        for item in result:
            print(f"  {item.field} ({item.type}): {item.value}")
            
    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")
        print("提示: 请确保 Ollama 服务正在运行并拉取了模型")
        print("      拉取模型: ollama pull llama2")
    
    # =====================================================
    # 示例 3: 使用 vLLM 本地服务
    # =====================================================
    print("\n" + "=" * 60)
    print("示例 3: vLLM (http://localhost:8000/v1)")
    print("=" * 60)
    
    request_vllm = ExtractRequest(
        source="raw",
        file="王五是一名产品经理，管理一个 10 人的团队，有 3 年的团队管理经验。",
        schema=[
            SchemaField(
                name="姓名",
                field="name",
                type="text",
                required=True,
            ),
            SchemaField(
                name="职位",
                field="position",
                type="text",
                required=True,
            ),
            SchemaField(
                name="团队规模",
                field="team_size",
                type="int",
                required=True,
            ),
            SchemaField(
                name="管理经验",
                field="management_experience",
                type="int",
                required=True,
            ),
        ],
        provider="custom",
        model="mistral-7b",  # vLLM 中的模型名称
        custom_base_url="http://localhost:8000/v1",
        custom_api_key="not-needed",
    )
    
    try:
        print("\n请求内容:")
        print(f"文本: {request_vllm.file}")
        print(f"提供商: {request_vllm.provider}")
        print(f"模型: {request_vllm.model}")
        print(f"API基础URL: {request_vllm.custom_base_url}")
        
        result = await extract_service.extract(request_vllm)
        
        print("\n提取结果:")
        for item in result:
            print(f"  {item.field} ({item.type}): {item.value}")
            
    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")
        print("提示: 请确保 vLLM 服务正在运行")
        print("      启动命令: python -m vllm.entrypoints.openai.api_server \\")
        print("                 --model mistral-7b")
    
    # =====================================================
    # 示例 4: 使用 LocalAI 本地服务
    # =====================================================
    print("\n" + "=" * 60)
    print("示例 4: LocalAI (http://localhost:8080/v1)")
    print("=" * 60)
    
    request_localai = ExtractRequest(
        source="raw",
        file="赵六在电商公司担任技术总监，年薪 50 万元，领导 30 人的技术团队。",
        schema=[
            SchemaField(
                name="姓名",
                field="name",
                type="text",
                required=True,
            ),
            SchemaField(
                name="职位",
                field="position",
                type="text",
                required=True,
            ),
            SchemaField(
                name="年薪",
                field="annual_salary",
                type="int",
                required=True,
            ),
            SchemaField(
                name="团队人数",
                field="team_members",
                type="int",
                required=True,
            ),
        ],
        provider="custom",
        model="ggml-gpt4all",  # LocalAI 中的模型名称
        custom_base_url="http://localhost:8080/v1",
        custom_api_key="not-needed",
    )
    
    try:
        print("\n请求内容:")
        print(f"文本: {request_localai.file}")
        print(f"提供商: {request_localai.provider}")
        print(f"模型: {request_localai.model}")
        print(f"API基础URL: {request_localai.custom_base_url}")
        
        result = await extract_service.extract(request_localai)
        
        print("\n提取结果:")
        for item in result:
            print(f"  {item.field} ({item.type}): {item.value}")
            
    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")
        print("提示: 请确保 LocalAI 服务正在运行")
        print("      Docker 启动: docker run -p 8080:8080 localai/localai:latest-aio-cpu")


async def check_service_health(base_url: str) -> bool:
    """检查服务是否正在运行"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/models", timeout=2.0)
            return response.status_code == 200
    except:
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Custom LLM 提供商使用示例")
    print("=" * 60)
    print("\n支持的本地 LLM 服务:")
    print("  1. LM Studio (http://localhost:1234/v1)")
    print("  2. Ollama (http://localhost:11434/v1)")
    print("  3. vLLM (http://localhost:8000/v1)")
    print("  4. LocalAI (http://localhost:8080/v1)")
    print("\n运行此脚本将尝试连接这些服务。")
    print("请确保相关服务已启动，否则会显示连接错误。")
    
    asyncio.run(main())
