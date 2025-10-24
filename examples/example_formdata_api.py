"""
FormData 提取 API 使用示例
"""
import asyncio
import aiohttp
import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def example_extract_with_formdata():
    """
    使用 FormData 调用提取 API
    """
    
    # 定义 schema
    schema = [
        {
            "name": "人名",
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
            "name": "职业",
            "field": "occupation",
            "type": "text",
            "required": True
        },
        {
            "name": "城市",
            "field": "city",
            "type": "text",
            "required": True
        }
    ]
    
    # 待提取的文本
    text_content = """
    张三，32岁，是一名资深的软件工程师。
    他目前在北京的一家知名科技公司工作。
    张三毕业于清华大学，拥有丰富的项目管理经验。
    """
    
    # 创建 FormData
    data = aiohttp.FormData()
    data.add_field("source", "raw")
    data.add_field("file", text_content)
    data.add_field("schema", json.dumps(schema, ensure_ascii=False))
    data.add_field("provider", "openai")
    data.add_field("model", "gpt-4o-mini")
    
    async with aiohttp.ClientSession() as session:
        try:
            logger.info("发送 FormData 请求到服务器...")
            async with session.post(
                "http://localhost:8000/extract",
                data=data,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info("✓ 请求成功")
                    logger.info(f"状态码: {result.get('code')}")
                    logger.info(f"消息: {result.get('message')}")
                    logger.info("提取结果:")
                    for item in result.get("data", []):
                        logger.info(f"  {item['field']}: {item['value']}")
                    return result
                else:
                    error = await response.json()
                    logger.error(f"✗ 请求失败: {response.status}")
                    logger.error(f"错误: {error}")
                    return None
        except Exception as e:
            logger.error(f"✗ 请求异常: {str(e)}")
            return None


async def example_extract_with_file_upload():
    """
    使用文件上传的方式
    """
    
    schema = [
        {
            "name": "标题",
            "field": "title",
            "type": "text",
            "required": True
        },
        {
            "name": "作者",
            "field": "author",
            "type": "text",
            "required": False
        }
    ]
    
    # 创建测试文件
    test_file_path = Path("test_document.txt")
    test_file_path.write_text("""
    标题: 机器学习基础概念
    作者: 张三
    
    机器学习是人工智能的一个重要分支。
    它通过数据学习规律，做出预测和决策。
    """, encoding="utf-8")
    
    data = aiohttp.FormData()
    data.add_field("source", "raw")
    data.add_field("schema", json.dumps(schema, ensure_ascii=False))
    data.add_field("provider", "openai")
    
    # 上传文件
    with open(test_file_path, "rb") as f:
        data.add_field("upload_file", f, filename=test_file_path.name)
        
        async with aiohttp.ClientSession() as session:
            try:
                logger.info("发送文件上传请求...")
                async with session.post(
                    "http://localhost:8000/extract",
                    data=data,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.info("✓ 文件上传成功")
                        logger.info("提取结果:")
                        for item in result.get("data", []):
                            logger.info(f"  {item['field']}: {item['value']}")
                        return result
                    else:
                        error = await response.json()
                        logger.error(f"✗ 文件上传失败: {response.status}")
                        logger.error(f"错误: {error}")
                        return None
            except Exception as e:
                logger.error(f"✗ 请求异常: {str(e)}")
                return None
            finally:
                # 清理测试文件
                if test_file_path.exists():
                    test_file_path.unlink()


async def example_custom_provider():
    """
    使用 Custom 提供商（OpenAI 兼容 API）
    """
    
    schema = [
        {
            "name": "公司名称",
            "field": "company_name",
            "type": "text",
            "required": True
        },
        {
            "name": "成立年份",
            "field": "founded_year",
            "type": "int",
            "required": False
        }
    ]
    
    text = "阿里巴巴是中国领先的电子商务和云计算公司，成立于1999年。"
    
    data = aiohttp.FormData()
    data.add_field("source", "raw")
    data.add_field("file", text)
    data.add_field("schema", json.dumps(schema, ensure_ascii=False))
    data.add_field("provider", "custom")
    # Custom 提供商的配置从环境变量读取，无需在请求中传递
    
    async with aiohttp.ClientSession() as session:
        try:
            logger.info("发送 Custom 提供商请求...")
            async with session.post(
                "http://localhost:8000/extract",
                data=data,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info("✓ Custom 提供商请求成功")
                    logger.info("提取结果:")
                    for item in result.get("data", []):
                        logger.info(f"  {item['field']}: {item['value']}")
                    return result
                else:
                    error = await response.json()
                    logger.error(f"✗ 请求失败: {response.status}")
                    logger.error(f"错误: {error}")
                    return None
        except Exception as e:
            logger.error(f"✗ 请求异常: {str(e)}")
            return None


async def main():
    """运行所有示例"""
    logger.info("=" * 80)
    logger.info("FormData API 使用示例")
    logger.info("=" * 80)
    
    # 示例 1：基本 FormData 请求
    logger.info("\n【示例 1】基本 FormData 请求")
    logger.info("-" * 80)
    await example_extract_with_formdata()
    
    # 示例 2：文件上传
    logger.info("\n【示例 2】文件上传")
    logger.info("-" * 80)
    await example_extract_with_file_upload()
    
    # 示例 3：Custom 提供商
    logger.info("\n【示例 3】Custom 提供商（OpenAI 兼容 API）")
    logger.info("-" * 80)
    await example_custom_provider()
    
    logger.info("\n" + "=" * 80)
    logger.info("所有示例执行完成")
    logger.info("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
