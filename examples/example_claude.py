"""
Anthropic Claude LLM 提供商使用示例
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


async def example_claude_basic():
    """
    示例：使用 Claude 提取基本信息
    
    注意：运行前需要设置以下环境变量：
    - ANTHROPIC_API_KEY
    """
    
    text = """
    李四是北京大学计算机科学系的一名研究生，年龄25岁。
    他的研究方向是机器学习和自然语言处理。
    李四已发表过5篇论文，其中2篇是一作。
    他的主要论文发表在 ICML 和 NeurIPS 上。
    李四的导师是王教授，他们在推荐系统方面有深入的研究。
    """
    
    schema = [
        SchemaField(name="姓名", field="name", type="text", required=True),
        SchemaField(name="年龄", field="age", type="int", required=True),
        SchemaField(name="学校", field="school", type="text", required=True),
        SchemaField(name="专业", field="major", type="text", required=True),
        SchemaField(name="学位", field="degree", type="text", required=True),
        SchemaField(name="研究方向", field="research_area", type="text", required=True),
        SchemaField(name="论文发表数", field="papers_count", type="int", required=False),
        SchemaField(name="顶会论文", field="top_conference", type="text", required=False),
    ]
    
    try:
        logger.info("使用 Claude 提取学生信息...")
        llm = LLMFactory.create("claude")
        
        # 显示可用模型
        logger.info("Claude 可用模型：")
        models = llm.get_available_models()
        for model in models:
            logger.info(f"  - {model.name}: {model.display_name}")
        
        # 验证连接
        logger.info("验证 Claude 连接...")
        is_connected = await llm.validate_connection()
        logger.info(f"连接状态: {'成功' if is_connected else '失败'}")
        
        if not is_connected:
            return None
        
        # 使用 Opus 进行提取（最强大的模型）
        result = await llm.extract(
            content=text,
            schema=schema,
            model="claude-3-opus-20240229",
        )
        
        logger.info("提取结果：")
        for item in result:
            logger.info(f"  {item.field}: {item.value}")
        
        return result
        
    except Exception as e:
        logger.error(f"错误: {str(e)}", exc_info=True)
        return None


async def example_claude_long_document():
    """
    示例：使用 Claude 处理长文档（利用 200K token 上下文窗口）
    Claude 3 支持长达 200K tokens 的上下文，非常适合处理长文档
    """
    
    # 模拟一个较长的文档
    long_document = """
    【年度报告 - 2023年财务总结】
    
    第一季度业绩：
    销售收入：1200万元
    成本支出：800万元
    利润：400万元
    市场占有率：12%
    
    第二季度业绩：
    销售收入：1500万元
    成本支出：900万元
    利润：600万元
    市场占有率：15%
    
    第三季度业绩：
    销售收入：1800万元
    成本支出：1000万元
    利润：800万元
    市场占有率：18%
    
    第四季度业绩：
    销售收入：2000万元
    成本支出：1100万元
    利润：900万元
    市场占有率：20%
    
    【全年总结】
    全年总销售收入：6500万元
    全年总成本支出：3800万元
    全年总利润：2700万元
    年末市场占有率：20%
    
    【主要成就】
    1. 成功推出 3 个新产品线
    2. 进入 5 个新的地理市场
    3. 建立了 15 个新的战略合作伙伴关系
    4. 员工增长 30%，现有员工 500 人
    5. 获得了行业最佳创新奖
    
    【存在的挑战】
    1. 供应链中断导致原材料成本上升 20%
    2. 主要竞争对手推出了低价产品
    3. 某些地区的监管政策变化
    
    【2024年展望】
    目标销售收入增长 25%，达到 8000 万元
    计划进入 8 个新市场
    研发投入增加 40%
    """
    
    schema = [
        SchemaField(name="全年总收入", field="annual_revenue", type="float", required=True),
        SchemaField(name="全年总利润", field="annual_profit", type="float", required=True),
        SchemaField(name="新产品线数", field="new_products", type="int", required=False),
        SchemaField(name="新市场数", field="new_markets", type="int", required=False),
        SchemaField(name="员工总数", field="employees", type="int", required=False),
        SchemaField(name="主要挑战", field="challenges", type="text", required=False),
    ]
    
    try:
        logger.info("使用 Claude 处理长文档...")
        llm = LLMFactory.create("claude")
        
        # 使用 Sonnet（更经济、更快，但仍然能处理长文档）
        result = await llm.extract(
            content=long_document,
            schema=schema,
            model="claude-3-sonnet-20240229",
        )
        
        logger.info("财务数据提取结果：")
        for item in result:
            logger.info(f"  {item.field}: {item.value}")
        
        return result
        
    except Exception as e:
        logger.error(f"错误: {str(e)}", exc_info=True)
        return None


async def example_claude_complex_reasoning():
    """
    示例：Claude 擅长复杂推理和分析
    """
    
    scenario = """
    甲公司和乙公司签订了一份合作协议。根据协议：
    
    1. 甲公司投资 500 万元，获得 30% 的股份
    2. 乙公司投资 800 万元，获得 50% 的股份
    3. 丙公司投资 300 万元，获得 20% 的股份
    
    半年后，公司获得了融资 2000 万元。根据协议，所有融资全部进入公司账户。
    
    问题：
    1. 原始估值是多少？
    2. 融资后各方的股份稀释比例是多少？
    3. 各方在融资中应该获得多少额外股份（假设均匀分配给原股东）？
    """
    
    schema = [
        SchemaField(name="原始公司估值", field="initial_valuation", type="float", required=True),
        SchemaField(name="甲公司融资后股份比例", field="company_a_stake", type="float", required=False),
        SchemaField(name="乙公司融资后股份比例", field="company_b_stake", type="float", required=False),
        SchemaField(name="丙公司融资后股份比例", field="company_c_stake", type="float", required=False),
        SchemaField(name="融资后总估值", field="post_funding_valuation", type="float", required=False),
    ]
    
    try:
        logger.info("使用 Claude 进行复杂推理分析...")
        llm = LLMFactory.create("claude")
        
        # 使用 Opus（最强的模型，最适合复杂推理）
        result = await llm.extract(
            content=scenario,
            schema=schema,
            model="claude-3-opus-20240229",
        )
        
        logger.info("投资分析结果：")
        for item in result:
            logger.info(f"  {item.field}: {item.value}")
        
        return result
        
    except Exception as e:
        logger.error(f"错误: {str(e)}", exc_info=True)
        return None


async def example_cost_comparison():
    """
    示例：展示不同 Claude 模型的成本对比
    """
    logger.info("Claude 模型成本对比：")
    logger.info("-" * 60)
    
    llm = LLMFactory.create("claude")
    models = llm.get_available_models()
    
    # 假设提取 1000 个输入 tokens 和 200 个输出 tokens
    input_tokens = 1000
    output_tokens = 200
    
    for model in models:
        if model.cost_per_1k_input:
            input_cost = (input_tokens / 1000) * (model.cost_per_1k_input or 0)
            output_cost = (output_tokens / 1000) * (model.cost_per_1k_output or 0)
            total_cost = input_cost + output_cost
            
            logger.info(f"{model.display_name}:")
            logger.info(f"  输入成本: ¥{input_cost:.6f}")
            logger.info(f"  输出成本: ¥{output_cost:.6f}")
            logger.info(f"  总成本: ¥{total_cost:.6f}")
            logger.info()


async def main():
    """运行所有示例"""
    logger.info("=" * 60)
    logger.info("Anthropic Claude LLM 使用示例")
    logger.info("=" * 60)
    
    # 示例 1：基本提取
    logger.info("\n【示例 1】提取学生信息")
    logger.info("-" * 60)
    await example_claude_basic()
    
    # 示例 2：长文档处理
    logger.info("\n【示例 2】处理长财务文档（利用 200K token 上下文）")
    logger.info("-" * 60)
    await example_claude_long_document()
    
    # 示例 3：复杂推理
    logger.info("\n【示例 3】复杂推理分析（投资计算）")
    logger.info("-" * 60)
    await example_claude_complex_reasoning()
    
    # 示例 4：成本对比
    logger.info("\n【示例 4】模型成本对比")
    logger.info("-" * 60)
    await example_cost_comparison()
    
    logger.info("\n" + "=" * 60)
    logger.info("所有示例执行完成")
    logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
