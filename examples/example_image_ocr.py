"""
图像 OCR 处理示例
演示如何使用系统的图像处理和 OCR 功能
"""
import asyncio
import aiohttp
import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def example_1_simple_image_ocr():
    """示例 1: 简单的图像 OCR 提取"""
    
    logger.info("=" * 80)
    logger.info("示例 1: 简单的图像 OCR 提取")
    logger.info("=" * 80)
    
    schema = [
        {
            "name": "图像内容",
            "field": "content",
            "type": "text",
            "required": True
        }
    ]
    
    data = aiohttp.FormData()
    data.add_field("source", "raw")
    data.add_field("schema", json.dumps(schema, ensure_ascii=False))
    data.add_field("provider", "openai")
    data.add_field("model", "gpt-4o-mini")
    
    # 上传图像文件 - 系统会自动进行 OCR
    image_path = Path("sample_image.png")
    if image_path.exists():
        with open(image_path, "rb") as f:
            data.add_field("upload_file", f, filename="sample_image.png")
            
            async with aiohttp.ClientSession() as session:
                try:
                    logger.info("发送图像上传请求...")
                    async with session.post(
                        "http://localhost:8000/extract",
                        data=data,
                        timeout=aiohttp.ClientTimeout(total=120)
                    ) as response:
                        if response.status == 200:
                            result = await response.json()
                            logger.info("✓ OCR 识别成功")
                            logger.info(f"识别文本长度: {sum(len(str(item.get('value', ''))) for item in result.get('data', []))} 字符")
                            for item in result.get("data", []):
                                logger.info(f"  {item['field']}: {item['value'][:100]}...")
                            return result
                        else:
                            error = await response.json()
                            logger.error(f"✗ 请求失败: {response.status}")
                            logger.error(f"错误: {error}")
                            return None
                except Exception as e:
                    logger.error(f"✗ 请求异常: {str(e)}")
                    return None
    else:
        logger.warning(f"⚠ 样本图像不存在: {image_path}")


async def example_2_invoice_recognition():
    """示例 2: 发票识别"""
    
    logger.info("\n" + "=" * 80)
    logger.info("示例 2: 发票识别")
    logger.info("=" * 80)
    
    schema = [
        {
            "name": "发票号",
            "field": "invoice_number",
            "type": "text",
            "required": True
        },
        {
            "name": "金额",
            "field": "amount",
            "type": "text",
            "required": True
        },
        {
            "name": "日期",
            "field": "invoice_date",
            "type": "text",
            "required": True
        },
        {
            "name": "公司名称",
            "field": "company_name",
            "type": "text",
            "required": False
        }
    ]
    
    data = aiohttp.FormData()
    data.add_field("source", "raw")
    data.add_field("schema", json.dumps(schema, ensure_ascii=False))
    data.add_field("provider", "openai")
    data.add_field("model", "gpt-4o-mini")
    
    invoice_path = Path("invoice.jpg")
    if invoice_path.exists():
        with open(invoice_path, "rb") as f:
            data.add_field("upload_file", f, filename="invoice.jpg")
            
            async with aiohttp.ClientSession() as session:
                try:
                    logger.info("开始识别发票...")
                    async with session.post(
                        "http://localhost:8000/extract",
                        data=data,
                        timeout=aiohttp.ClientTimeout(total=120)
                    ) as response:
                        if response.status == 200:
                            result = await response.json()
                            logger.info("✓ 发票识别成功")
                            logger.info("提取的发票信息:")
                            for item in result.get("data", []):
                                logger.info(f"  {item['field']}: {item['value']}")
                            return result
                        else:
                            logger.error(f"✗ 发票识别失败: {response.status}")
                            return None
                except Exception as e:
                    logger.error(f"✗ 请求异常: {str(e)}")
                    return None
    else:
        logger.warning(f"⚠ 发票样本不存在: {invoice_path}")


async def example_3_document_scan():
    """示例 3: 文档扫描识别"""
    
    logger.info("\n" + "=" * 80)
    logger.info("示例 3: 文档扫描识别")
    logger.info("=" * 80)
    
    schema = [
        {
            "name": "标题",
            "field": "title",
            "type": "text",
            "required": True
        },
        {
            "name": "正文内容",
            "field": "content",
            "type": "text",
            "required": False
        },
        {
            "name": "作者",
            "field": "author",
            "type": "text",
            "required": False
        },
        {
            "name": "日期",
            "field": "date",
            "type": "text",
            "required": False
        }
    ]
    
    data = aiohttp.FormData()
    data.add_field("source", "raw")
    data.add_field("schema", json.dumps(schema, ensure_ascii=False))
    data.add_field("provider", "openai")
    data.add_field("model", "gpt-4o-mini")
    
    document_path = Path("document_scan.png")
    if document_path.exists():
        with open(document_path, "rb") as f:
            data.add_field("upload_file", f, filename="document_scan.png")
            
            async with aiohttp.ClientSession() as session:
                try:
                    logger.info("开始识别扫描文档...")
                    async with session.post(
                        "http://localhost:8000/extract",
                        data=data,
                        timeout=aiohttp.ClientTimeout(total=120)
                    ) as response:
                        if response.status == 200:
                            result = await response.json()
                            logger.info("✓ 文档识别成功")
                            logger.info("提取的文档信息:")
                            for item in result.get("data", []):
                                value = item['value']
                                if isinstance(value, str) and len(value) > 50:
                                    value = value[:50] + "..."
                                logger.info(f"  {item['field']}: {value}")
                            return result
                        else:
                            logger.error(f"✗ 文档识别失败: {response.status}")
                            return None
                except Exception as e:
                    logger.error(f"✗ 请求异常: {str(e)}")
                    return None
    else:
        logger.warning(f"⚠ 扫描文档样本不存在: {document_path}")


async def example_4_batch_image_processing():
    """示例 4: 批量图像处理"""
    
    logger.info("\n" + "=" * 80)
    logger.info("示例 4: 批量图像处理")
    logger.info("=" * 80)
    
    schema = [
        {
            "name": "内容",
            "field": "content",
            "type": "text"
        }
    ]
    
    # 获取所有图像文件
    image_dir = Path("./images")
    image_files = []
    if image_dir.exists():
        image_files = list(image_dir.glob("*.png")) + list(image_dir.glob("*.jpg"))
    
    if not image_files:
        logger.warning("⚠ 图像目录不存在或为空")
        return
    
    logger.info(f"找到 {len(image_files)} 个图像文件，开始批处理...")
    
    results = {}
    async with aiohttp.ClientSession() as session:
        for i, image_file in enumerate(image_files, 1):
            logger.info(f"[{i}/{len(image_files)}] 处理 {image_file.name}...")
            
            data = aiohttp.FormData()
            data.add_field("source", "raw")
            data.add_field("schema", json.dumps(schema, ensure_ascii=False))
            data.add_field("provider", "openai")
            
            with open(image_file, "rb") as f:
                data.add_field("upload_file", f, filename=image_file.name)
                
                try:
                    async with session.post(
                        "http://localhost:8000/extract",
                        data=data,
                        timeout=aiohttp.ClientTimeout(total=120)
                    ) as response:
                        if response.status == 200:
                            result = await response.json()
                            results[image_file.name] = {
                                "status": "success",
                                "data": result.get("data", [])
                            }
                            logger.info(f"  ✓ 成功")
                        else:
                            results[image_file.name] = {"status": "failed"}
                            logger.info(f"  ✗ 失败 (HTTP {response.status})")
                except Exception as e:
                    results[image_file.name] = {"status": "error", "error": str(e)}
                    logger.error(f"  ✗ 异常: {str(e)}")
    
    logger.info("\n批处理完成，总结:")
    success_count = sum(1 for r in results.values() if r.get("status") == "success")
    logger.info(f"  成功: {success_count}/{len(results)}")
    return results


async def example_5_image_with_ocr_comparison():
    """示例 5: 同一张图像的不同处理方式对比"""
    
    logger.info("\n" + "=" * 80)
    logger.info("示例 5: 图像处理流程对比")
    logger.info("=" * 80)
    
    schema = [
        {
            "name": "识别内容",
            "field": "recognized_text",
            "type": "text"
        }
    ]
    
    data = aiohttp.FormData()
    data.add_field("source", "raw")
    data.add_field("schema", json.dumps(schema, ensure_ascii=False))
    data.add_field("provider", "openai")
    
    test_image = Path("test_image.png")
    if test_image.exists():
        with open(test_image, "rb") as f:
            data.add_field("upload_file", f, filename="test_image.png")
            
            async with aiohttp.ClientSession() as session:
                try:
                    logger.info("1. 发送上传请求...")
                    async with session.post(
                        "http://localhost:8000/extract",
                        data=data,
                        timeout=aiohttp.ClientTimeout(total=120)
                    ) as response:
                        logger.info(f"2. 响应状态: {response.status}")
                        
                        if response.status == 200:
                            result = await response.json()
                            logger.info("3. 处理完成")
                            logger.info("\n📊 处理结果:")
                            logger.info(f"  返回数据项: {len(result.get('data', []))}")
                            for item in result.get("data", []):
                                logger.info(f"  - {item['field']}: {str(item['value'])[:80]}")
                        else:
                            logger.error(f"处理失败: {response.status}")
                
                except Exception as e:
                    logger.error(f"✗ 请求异常: {str(e)}")
    else:
        logger.warning(f"⚠ 测试图像不存在: {test_image}")


async def main():
    """运行所有示例"""
    logger.info("\n")
    logger.info("╔" + "=" * 78 + "╗")
    logger.info("║" + " " * 20 + "图像 OCR 处理示例" + " " * 42 + "║")
    logger.info("╚" + "=" * 78 + "╝")
    
    # 运行示例
    await example_1_simple_image_ocr()
    await example_2_invoice_recognition()
    await example_3_document_scan()
    await example_4_batch_image_processing()
    await example_5_image_with_ocr_comparison()
    
    logger.info("\n")
    logger.info("╔" + "=" * 78 + "╗")
    logger.info("║" + " " * 25 + "所有示例执行完成" + " " * 37 + "║")
    logger.info("╚" + "=" * 78 + "╝\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n程序被用户中断")
    except Exception as e:
        logger.error(f"程序运行出错: {str(e)}", exc_info=True)
