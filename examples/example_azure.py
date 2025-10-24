"""
Azure OpenAI LLM 提供商使用示例
"""
import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.models import SchemaField, ExtractRequest
from app.llm import LLMFactory
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def example_azure_extract():
    """
    示例：使用 Azure OpenAI 提取人员信息
    
    注意：运行前需要设置以下环境变量：
    - AZURE_OPENAI_KEY
    - AZURE_OPENAI_ENDPOINT
    - AZURE_OPENAI_API_VERSION
    - AZURE_OPENAI_DEPLOYMENT
    """
    
    # 准备数据
    text_content = """
    张三，男，32岁，是一名资深软件工程师。
    他毕业于清华大学计算机科学系，2015年加入阿里巴巴。
    目前担任高级技术专家，主要负责分布式系统的开发工作。
    他的技能包括 Java、Python、Go、C++ 等编程语言。
    联系方式：zhangsan@example.com
    """
    
    # 定义 Schema
    schema = [
        SchemaField(name="姓名", field="name", type="text", required=True),
        SchemaField(name="性别", field="gender", type="text", required=True),
        SchemaField(name="年龄", field="age", type="int", required=True),
        SchemaField(name="职位", field="position", type="text", required=True),
        SchemaField(name="公司", field="company", type="text", required=True),
        SchemaField(name="学校", field="university", type="text", required=True),
        SchemaField(name="入职年份", field="join_year", type="int", required=False),
        SchemaField(name="邮箱", field="email", type="text", required=False),
        SchemaField(name="编程语言", field="languages", type="text", required=False),
    ]
    
    try:
        # 创建 Azure OpenAI LLM 实例
        logger.info("正在创建 Azure OpenAI LLM 实例...")
        llm = LLMFactory.create("azure")
        
        # 显示可用模型
        logger.info("获取可用模型...")
        available_models = llm.get_available_models()
        for model in available_models:
            logger.info(f"  - {model.name} ({model.display_name})")
        
        # 验证连接
        logger.info("验证 Azure OpenAI 连接...")
        is_connected = await llm.validate_connection()
        if not is_connected:
            logger.error("连接验证失败！")
            return
        logger.info("连接验证成功！")
        
        # 执行提取
        logger.info("开始提取数据...")
        result = await llm.extract(
            content=text_content,
            schema=schema,
            model="gpt-4",  # 使用 Azure 部署的模型名
        )
        
        # 显示结果
        logger.info("数据提取完成：")
        for item in result:
            logger.info(f"  {item.field}: {item.value}")
        
        return result
        
    except Exception as e:
        logger.error(f"错误: {str(e)}", exc_info=True)
        return None


async def example_azure_document_extract():
    """
    示例：使用 Azure OpenAI 从长文档提取信息
    """
    
    document = """
    【合同信息】
    合同编号：CT-2024-001
    签订日期：2024年1月15日
    合同甲方：北京科技有限公司
    合同乙方：上海开发公司
    
    【主要条款】
    1. 项目内容
    本项目为云平台开发项目，预计耗时12个月。
    
    2. 合同金额
    总合同金额：500万元人民币
    付款方式：分3期支付，每期支付金额为166.7万元
    
    3. 时间安排
    项目启动：2024年2月1日
    项目完成：2025年1月31日
    
    4. 责任方
    甲方负责需求确认和验收工作
    乙方负责开发、测试和上线工作
    """
    
    schema = [
        SchemaField(name="合同编号", field="contract_no", type="text", required=True),
        SchemaField(name="签订日期", field="sign_date", type="date", required=True),
        SchemaField(name="甲方", field="party_a", type="text", required=True),
        SchemaField(name="乙方", field="party_b", type="text", required=True),
        SchemaField(name="合同金额", field="amount", type="float", required=True),
        SchemaField(name="项目周期（月）", field="duration_months", type="int", required=True),
        SchemaField(name="启动日期", field="start_date", type="date", required=True),
        SchemaField(name="完成日期", field="completion_date", type="date", required=True),
    ]
    
    try:
        logger.info("从长文档提取合同信息...")
        llm = LLMFactory.create("azure")
        
        result = await llm.extract(
            content=document,
            schema=schema,
            model="gpt-4",
        )
        
        logger.info("合同信息提取完成：")
        for item in result:
            logger.info(f"  {item.field}: {item.value}")
        
        return result
        
    except Exception as e:
        logger.error(f"错误: {str(e)}", exc_info=True)
        return None


async def main():
    """运行示例"""
    logger.info("=" * 50)
    logger.info("Azure OpenAI LLM 使用示例")
    logger.info("=" * 50)
    
    # 示例 1：提取人员信息
    logger.info("\n【示例 1】提取人员信息")
    logger.info("-" * 50)
    await example_azure_extract()
    
    # 示例 2：提取文档信息
    logger.info("\n【示例 2】提取合同信息")
    logger.info("-" * 50)
    await example_azure_document_extract()
    
    logger.info("\n" + "=" * 50)
    logger.info("所有示例执行完成")
    logger.info("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
