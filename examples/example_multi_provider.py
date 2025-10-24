"""
多 LLM 提供商对比示例
对比 OpenAI、Azure OpenAI、Claude、Gemini 在数据提取任务上的表现
"""
import asyncio
import sys
import time
from pathlib import Path
from typing import Dict, List

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.models import SchemaField, ExtractedValue
from app.llm import LLMFactory
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MultiProviderComparison:
    """多提供商对比工具"""
    
    def __init__(self):
        self.providers = ["openai", "azure", "claude", "gemini"]
        self.results = {}
    
    async def run_comparison(self, text: str, schema: List[SchemaField], models: Dict[str, str]):
        """
        运行多提供商对比
        
        Args:
            text: 待提取的文本
            schema: 提取 schema
            models: 各提供商使用的模型 {provider: model_name}
        """
        logger.info("=" * 80)
        logger.info("多 LLM 提供商对比测试")
        logger.info("=" * 80)
        logger.info(f"待提取文本长度: {len(text)} 字符")
        logger.info(f"Schema 字段数: {len(schema)}")
        logger.info()
        
        results = {}
        
        for provider in self.providers:
            if provider not in models:
                logger.warning(f"跳过 {provider}，未指定模型")
                continue
            
            logger.info(f"正在测试 {provider.upper()} 提供商...")
            logger.info("-" * 80)
            
            try:
                result = await self._test_provider(
                    provider=provider,
                    model=models[provider],
                    text=text,
                    schema=schema,
                )
                results[provider] = result
                
            except Exception as e:
                logger.error(f"错误: {str(e)}")
                results[provider] = {"error": str(e)}
            
            logger.info()
        
        self.results = results
        return results
    
    async def _test_provider(
        self,
        provider: str,
        model: str,
        text: str,
        schema: List[SchemaField],
    ) -> Dict:
        """测试单个提供商"""
        
        start_time = time.time()
        
        try:
            # 创建 LLM 实例
            llm = LLMFactory.create(provider)
            
            # 获取可用模型
            available_models = llm.get_available_models()
            logger.info(f"可用模型: {len(available_models)} 个")
            
            # 验证连接
            is_connected = await llm.validate_connection()
            if not is_connected:
                logger.warning(f"连接验证失败")
                return {"error": "连接验证失败"}
            
            logger.info("连接验证: ✓ 成功")
            
            # 执行提取
            logger.info(f"使用模型: {model}")
            logger.info("开始提取数据...")
            
            extraction_start = time.time()
            extracted = await llm.extract(
                content=text,
                schema=schema,
                model=model,
            )
            extraction_time = time.time() - extraction_start
            
            total_time = time.time() - start_time
            
            # 统计结果
            success_count = sum(1 for item in extracted if item.value is not None)
            
            result = {
                "success": True,
                "model": model,
                "total_time": total_time,
                "extraction_time": extraction_time,
                "extracted_fields": len(extracted),
                "success_fields": success_count,
                "success_rate": f"{(success_count/len(extracted)*100):.1f}%",
                "data": extracted,
            }
            
            # 输出结果摘要
            logger.info(f"提取完成: {success_count}/{len(extracted)} 字段")
            logger.info(f"总耗时: {total_time:.2f}s")
            logger.info(f"提取耗时: {extraction_time:.2f}s")
            logger.info(f"成功率: {result['success_rate']}")
            
            return result
            
        except Exception as e:
            logger.error(f"测试失败: {str(e)}")
            raise
    
    def print_summary(self):
        """打印对比总结"""
        if not self.results:
            logger.warning("没有测试结果")
            return
        
        logger.info("=" * 100)
        logger.info("对比总结")
        logger.info("=" * 100)
        
        # 创建对比表
        logger.info(f"{'提供商':<12} {'模型':<25} {'耗时(s)':<12} {'字段数':<10} {'成功率':<10} {'状态':<10}")
        logger.info("-" * 100)
        
        for provider, result in self.results.items():
            if "error" in result:
                logger.info(f"{provider:<12} {'错误':<25} {'-':<12} {'-':<10} {'-':<10} {'✗':<10}")
            else:
                model = result.get("model", "")[:20]
                time_taken = f"{result.get('total_time', 0):.2f}"
                fields = f"{result.get('extracted_fields', 0)}"
                success_rate = result.get("success_rate", "N/A")
                status = "✓" if result.get("success") else "✗"
                
                logger.info(f"{provider:<12} {model:<25} {time_taken:<12} {fields:<10} {success_rate:<10} {status:<10}")
        
        logger.info("-" * 100)
        
        # 找出最快的提供商
        valid_results = {p: r for p, r in self.results.items() if "error" not in r}
        if valid_results:
            fastest = min(valid_results.items(), key=lambda x: x[1]["total_time"])
            logger.info(f"\n✓ 最快提供商: {fastest[0].upper()} ({fastest[1]['total_time']:.2f}s)")
            
            best_success = max(valid_results.items(), 
                             key=lambda x: float(x[1]["success_rate"].rstrip("%")))
            logger.info(f"✓ 最高成功率: {best_success[0].upper()} ({best_success[1]['success_rate']})")
    
    def print_detailed_results(self):
        """打印详细结果"""
        for provider, result in self.results.items():
            logger.info("\n" + "=" * 80)
            logger.info(f"{provider.upper()} 详细结果")
            logger.info("=" * 80)
            
            if "error" in result:
                logger.info(f"错误: {result['error']}")
                continue
            
            logger.info(f"模型: {result['model']}")
            logger.info(f"耗时: {result['total_time']:.2f}s")
            logger.info(f"提取字段: {result['extracted_fields']}")
            logger.info(f"成功率: {result['success_rate']}")
            logger.info()
            logger.info("提取数据：")
            
            for item in result.get("data", []):
                status = "✓" if item.value is not None else "✗"
                value_str = str(item.value)[:50] if item.value else "null"
                logger.info(f"  {status} {item.field}: {value_str}")


async def example_basic_comparison():
    """示例：基本数据提取对比"""
    
    text = """
    李明是一名资深的软件架构师，现年38岁。
    他拥有清华大学的硕士学位，专业是计算机科学。
    李明在 Google 和 Meta 分别工作过 5 年和 3 年。
    他目前的月薪是 8 万元，年度奖金是 50 万元。
    李明已发表过 15 篇学术论文，其中 5 篇是第一作者。
    他的研究方向主要包括分布式系统和云计算。
    """
    
    schema = [
        SchemaField(name="姓名", field="name", type="text", required=True),
        SchemaField(name="年龄", field="age", type="int", required=True),
        SchemaField(name="学历", field="education", type="text", required=True),
        SchemaField(name="专业", field="major", type="text", required=True),
        SchemaField(name="工作经验", field="experience", type="text", required=True),
        SchemaField(name="月薪", field="monthly_salary", type="int", required=False),
        SchemaField(name="年度奖金", field="annual_bonus", type="int", required=False),
        SchemaField(name="论文总数", field="papers", type="int", required=False),
        SchemaField(name="第一作者论文数", field="first_author_papers", type="int", required=False),
        SchemaField(name="研究方向", field="research_areas", type="text", required=False),
    ]
    
    models = {
        "openai": "gpt-4o-mini",
        "azure": "gpt-4",
        "claude": "claude-3-sonnet-20240229",
        "gemini": "gemini-2.0-flash",
    }
    
    comparison = MultiProviderComparison()
    results = await comparison.run_comparison(text, schema, models)
    comparison.print_summary()
    comparison.print_detailed_results()
    
    return results


async def example_document_complexity():
    """示例：处理复杂文档的对比"""
    
    # 模拟一份复杂的商业合同
    complex_document = """
    【中华人民共和国合同】
    
    合同编号：2024-BIZ-001
    签订日期：2024年1月15日
    合同生效日期：2024年2月1日
    
    甲方（发包方）：北京创新科技有限公司
    地址：北京市朝阳区建国路1号
    法定代表人：张三
    联系电话：010-12345678
    
    乙方（承包方）：上海智能解决方案有限公司
    地址：上海市浦东新区世纪大道100号
    法定代表人：李四
    联系电话：021-87654321
    
    【合作内容】
    甲乙双方就如下项目达成一致意见：
    项目名称：《企业级 AI 平台开发项目》
    项目周期：24 个月
    项目阶段：
    第一阶段（0-6 个月）：需求分析和系统架构设计
    第二阶段（6-12 个月）：核心功能开发
    第三阶段（12-18 个月）：功能完善和测试
    第四阶段（18-24 个月）：上线和维护
    
    【合同金额】
    项目总金额：5000万元人民币（含税）
    其中：
    - 第一阶段：600 万元
    - 第二阶段：1600 万元
    - 第三阶段：1200 万元
    - 第四阶段：1600 万元
    
    付款方式：分期支付
    - 签订合同后 7 天内：支付 20% 即 1000 万元
    - 第一阶段完成后：支付 20% 即 1000 万元
    - 第二阶段完成后：支付 30% 即 1500 万元
    - 项目完成后：支付 30% 即 1500 万元
    
    【违约责任】
    若甲方逾期支付，每日按未支付金额的 0.05% 计算违约金。
    若乙方无法按期完成各阶段工作，每延迟一天支付违约金 50000 元。
    
    【保密条款】
    合作双方应对本项目中获取的所有信息和数据进行保密，
    保密期限为项目完成后 5 年。
    
    【争议解决】
    若产生争议，双方首先通过友好协商解决；
    协商不成的，提交北京仲裁委员会仲裁。
    
    【其他条款】
    1. 本合同自双方签章之日起生效
    2. 本合同一式两份，具有同等法律效力
    3. 本合同未尽事宜由双方另行协商确定
    """
    
    schema = [
        SchemaField(name="合同编号", field="contract_no", type="text", required=True),
        SchemaField(name="签订日期", field="sign_date", type="date", required=True),
        SchemaField(name="生效日期", field="effective_date", type="date", required=True),
        SchemaField(name="甲方名称", field="party_a", type="text", required=True),
        SchemaField(name="乙方名称", field="party_b", type="text", required=True),
        SchemaField(name="项目名称", field="project_name", type="text", required=True),
        SchemaField(name="项目周期月数", field="duration_months", type="int", required=True),
        SchemaField(name="项目总金额万元", field="total_amount", type="float", required=True),
        SchemaField(name="支付期数", field="payment_times", type="int", required=False),
        SchemaField(name="逾期违约金比例", field="penalty_rate", type="float", required=False),
        SchemaField(name="保密期限年数", field="confidentiality_years", type="int", required=False),
    ]
    
    models = {
        "openai": "gpt-4o",
        "azure": "gpt-4",
        "claude": "claude-3-opus-20240229",
        "gemini": "gemini-1.5-pro",
    }
    
    logger.info("\n" + "=" * 80)
    logger.info("【测试 2】复杂文档处理对比")
    logger.info("=" * 80)
    
    comparison = MultiProviderComparison()
    results = await comparison.run_comparison(complex_document, schema, models)
    comparison.print_summary()
    
    return results


async def main():
    """运行所有对比示例"""
    logger.info("=" * 80)
    logger.info("多 LLM 提供商性能对比")
    logger.info("=" * 80)
    
    # 测试 1：基本对比
    logger.info("\n【测试 1】基本数据提取对比")
    logger.info("=" * 80)
    await example_basic_comparison()
    
    # 测试 2：复杂文档处理
    logger.info("\n\n【测试 2】复杂文档处理对比")
    logger.info("=" * 80)
    await example_document_complexity()
    
    logger.info("\n\n" + "=" * 80)
    logger.info("所有对比测试完成")
    logger.info("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
