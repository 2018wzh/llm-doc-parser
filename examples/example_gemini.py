"""
Google Gemini LLM 提供商使用示例
"""
import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.models import SchemaField
from app.llm import LLMFactory
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def example_gemini_basic():
    """
    示例：使用 Gemini 提取基本信息
    
    注意：运行前需要设置以下环境变量：
    - GOOGLE_API_KEY
    """
    
    text = """
    王五是一名产品经理，现在在一家科技公司工作。
    他从事产品工作已经有5年的经验，先后负责过3个产品线。
    王五最为成功的产品线年收入达到了1000万元。
    他的核心竞争力在于用户研究和数据分析。
    王五的教育背景是北京工业大学，工业设计专业。
    """
    
    schema = [
        SchemaField(name="姓名", field="name", type="text", required=True),
        SchemaField(name="职位", field="position", type="text", required=True),
        SchemaField(name="工作年限", field="years_experience", type="int", required=True),
        SchemaField(name="负责产品线数", field="product_lines", type="int", required=False),
        SchemaField(name="最成功产品年收入", field="best_product_revenue", type="float", required=False),
        SchemaField(name="大学", field="university", type="text", required=False),
        SchemaField(name="专业", field="major", type="text", required=False),
    ]
    
    try:
        logger.info("使用 Gemini 提取产品经理信息...")
        llm = LLMFactory.create("gemini")
        
        # 显示可用模型
        logger.info("Gemini 可用模型：")
        models = llm.get_available_models()
        for model in models:
            logger.info(f"  - {model.name}: {model.display_name}")
        
        # 验证连接
        logger.info("验证 Gemini 连接...")
        is_connected = await llm.validate_connection()
        logger.info(f"连接状态: {'成功' if is_connected else '失败'}")
        
        if not is_connected:
            return None
        
        # 使用最新的 Gemini 2.0 Flash
        result = await llm.extract(
            content=text,
            schema=schema,
            model="gemini-2.0-flash",
        )
        
        logger.info("提取结果：")
        for item in result:
            logger.info(f"  {item.field}: {item.value}")
        
        return result
        
    except Exception as e:
        logger.error(f"错误: {str(e)}", exc_info=True)
        return None


async def example_gemini_multimodal():
    """
    示例：Gemini 的多模态能力
    注意：当前示例仅展示架构，实际图像处理需要调整
    """
    logger.info("Gemini 多模态能力演示")
    logger.info("-" * 60)
    logger.info("Gemini 2.0 Flash 和 1.5 Pro 支持多模态处理，包括：")
    logger.info("  - 图像识别和分析")
    logger.info("  - 文档扫描 OCR")
    logger.info("  - 图表数据提取")
    logger.info("  - 视频帧分析")
    logger.info()
    logger.info("未来版本将支持直接的图像提取功能")
    logger.info("相关文档：https://ai.google.dev/docs/vision")


async def example_gemini_cost_effective():
    """
    示例：使用经济高效的 Gemini 模型
    Gemini 是最具成本效益的选择，特别是高容量应用
    """
    
    text = """
    截至2024年1月，全球科技公司市值排名：
    1. Apple Inc. - 3.2万亿美元
    2. Saudi Aramco - 2.5万亿美元
    3. Microsoft Corporation - 3.1万亿美元
    4. Alphabet Inc. (Google) - 1.8万亿美元
    5. Amazon.com Inc. - 1.7万亿美元
    6. NVIDIA Corporation - 1.3万亿美元
    7. Tesla Inc. - 0.8万亿美元
    8. Meta Platforms Inc. - 1.2万亿美元
    
    这些公司在过去一年中都经历了显著的增长。
    特别是AI相关公司如NVIDIA和Microsoft表现突出。
    """
    
    schema = [
        SchemaField(name="排名", field="rank", type="int", required=True),
        SchemaField(name="公司名称", field="company_name", type="text", required=True),
        SchemaField(name="市值万亿美元", field="market_cap", type="float", required=True),
    ]
    
    try:
        logger.info("使用成本高效的 Gemini 1.5 Flash 提取市值数据...")
        llm = LLMFactory.create("gemini")
        
        # 使用 Flash 模型（最经济）
        result = await llm.extract(
            content=text,
            schema=schema,
            model="gemini-1.5-flash",
        )
        
        logger.info("市值排名数据提取：")
        for item in result:
            logger.info(f"  {item.field}: {item.value}")
        
        return result
        
    except Exception as e:
        logger.error(f"错误: {str(e)}", exc_info=True)
        return None


async def example_gemini_models_comparison():
    """
    示例：Gemini 不同模型的特点对比
    """
    logger.info("Gemini 模型对比分析")
    logger.info("-" * 80)
    logger.info(f"{'模型':<20} {'速度':<10} {'能力':<15} {'成本':<10} {'推荐场景':<25}")
    logger.info("-" * 80)
    
    llm = LLMFactory.create("gemini")
    models = llm.get_available_models()
    
    for model in models:
        if "2.0-flash" in model.name:
            speed = "极快"
            capability = "很高"
            cost = "很低"
            use_case = "高容量生产应用"
        elif "1.5-pro" in model.name:
            speed = "快"
            capability = "最高"
            cost = "中等"
            use_case = "复杂推理和分析"
        else:  # 1.5-flash
            speed = "很快"
            capability = "高"
            cost = "低"
            use_case = "成本敏感应用"
        
        logger.info(f"{model.name:<20} {speed:<10} {capability:<15} {cost:<10} {use_case:<25}")
    
    logger.info("-" * 80)
    logger.info("✓ 推荐首选：Gemini 2.0 Flash（最新、最快、最便宜）")
    logger.info("✓ 复杂任务：Gemini 1.5 Pro（最强大的推理能力）")
    logger.info("✓ 小型任务：Gemini 1.5 Flash（轻量级、经济）")


async def example_gemini_performance():
    """
    示例：展示 Gemini 的性能特点
    """
    logger.info("Gemini 性能特点")
    logger.info("-" * 60)
    logger.info("优势：")
    logger.info("  ✓ 速度快：平均响应时间 < 500ms")
    logger.info("  ✓ 成本低：比 GPT-4 便宜 80%+")
    logger.info("  ✓ 模型新：Gemini 2.0 是最新发布的前沿模型")
    logger.info("  ✓ 多模态：原生支持图像、视频分析")
    logger.info("  ✓ 上下文：支持百万级 token 上下文（某些版本）")
    logger.info()
    logger.info("适用场景：")
    logger.info("  • 高并发、大规模数据处理")
    logger.info("  • 成本敏感型应用")
    logger.info("  • 实时系统（需要低延迟）")
    logger.info("  • 多模态内容分析")
    logger.info("  • 快速原型开发")


async def example_billing_estimate():
    """
    示例：Gemini 成本估算
    """
    logger.info("Gemini 成本估算")
    logger.info("-" * 60)
    
    # 示例：100万个请求，每个 1000 token 输入，200 token 输出
    requests = 1_000_000
    input_tokens_per_request = 1000
    output_tokens_per_request = 200
    
    llm = LLMFactory.create("gemini")
    models = llm.get_available_models()
    
    total_input_tokens = requests * input_tokens_per_request
    total_output_tokens = requests * output_tokens_per_request
    
    for model in models:
        if model.cost_per_1k_input and model.cost_per_1k_output:
            input_cost = (total_input_tokens / 1_000_000) * (model.cost_per_1k_input * 1000)
            output_cost = (total_output_tokens / 1_000_000) * (model.cost_per_1k_output * 1000)
            total_cost = input_cost + output_cost
            
            logger.info(f"{model.display_name}:")
            logger.info(f"  输入成本: ¥{input_cost:.2f} ({total_input_tokens:,} tokens @ ${model.cost_per_1k_input}/1K)")
            logger.info(f"  输出成本: ¥{output_cost:.2f} ({total_output_tokens:,} tokens @ ${model.cost_per_1k_output}/1K)")
            logger.info(f"  总成本: ¥{total_cost:.2f}")
            logger.info(f"  平均每个请求: ¥{total_cost/requests:.6f}")
            logger.info()


async def main():
    """运行所有示例"""
    logger.info("=" * 80)
    logger.info("Google Gemini LLM 使用示例")
    logger.info("=" * 80)
    
    # 示例 1：基本提取
    logger.info("\n【示例 1】提取产品经理信息")
    logger.info("-" * 80)
    await example_gemini_basic()
    
    # 示例 2：多模态能力
    logger.info("\n【示例 2】多模态能力演示")
    logger.info("-" * 80)
    await example_gemini_multimodal()
    
    # 示例 3：成本高效
    logger.info("\n【示例 3】成本高效的数据提取")
    logger.info("-" * 80)
    await example_gemini_cost_effective()
    
    # 示例 4：模型对比
    logger.info("\n【示例 4】Gemini 模型对比")
    logger.info("-" * 80)
    await example_gemini_models_comparison()
    
    # 示例 5：性能特点
    logger.info("\n【示例 5】性能特点分析")
    logger.info("-" * 80)
    await example_gemini_performance()
    
    # 示例 6：成本估算
    logger.info("\n【示例 6】大规模应用成本估算")
    logger.info("-" * 80)
    await example_billing_estimate()
    
    logger.info("\n" + "=" * 80)
    logger.info("所有示例执行完成")
    logger.info("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
