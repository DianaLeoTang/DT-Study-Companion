"""系统测试脚本"""
import sys
import os
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from loguru import logger
from src.workflow.agent_graph import TextbookAssistant
import time

def test_queries():
    """测试多个查询"""
    
    test_cases = [
        {
            "query": "流行病学第7版，什么是队列研究？",
            "expected_book": "流行病学",
            "expected_version": "7"
        },
        {
            "query": "生理学第9版中关于心脏的内容",
            "expected_book": "生理学",
            "expected_version": "9"
        },
        {
            "query": "病理学第8版讲了什么是炎症",
            "expected_book": "病理学",
            "expected_version": "8"
        },
        {
            "query": "流行病学中队列研究的优点",  # 未指定版本
            "expected_book": "流行病学",
            "expected_version": ""  # 应使用最新版
        }
    ]
    
    logger.info("="*60)
    logger.info("开始系统测试")
    logger.info("="*60)
    
    # 初始化助手
    try:
        assistant = TextbookAssistant()
        logger.info("✓ 助手初始化成功\n")
    except Exception as e:
        logger.error(f"✗ 助手初始化失败: {e}")
        return False
    
    # 测试每个查询
    success_count = 0
    failed_cases = []
    
    for i, test_case in enumerate(test_cases, 1):
        query = test_case["query"]
        
        logger.info(f"\n{'='*60}")
        logger.info(f"测试 {i}/{len(test_cases)}: {query}")
        logger.info(f"{'='*60}")
        
        start_time = time.time()
        
        try:
            result = assistant.query(query)
            elapsed = time.time() - start_time
            
            # 验证结果
            checks = []
            
            # 检查书名
            if result["book_name"] == test_case["expected_book"]:
                checks.append("✓ 书名正确")
            else:
                checks.append(f"✗ 书名错误: 期望{test_case['expected_book']}, 实际{result['book_name']}")
            
            # 检查版本（如果指定了）
            if test_case["expected_version"]:
                if result["version"] == test_case["expected_version"]:
                    checks.append("✓ 版本正确")
                else:
                    checks.append(f"✗ 版本错误: 期望{test_case['expected_version']}, 实际{result['version']}")
            
            # 检查答案
            if result["answer"] and len(result["answer"]) > 50:
                checks.append("✓ 答案生成成功")
            else:
                checks.append("✗ 答案过短或为空")
            
            # 检查来源
            if result["sources"]:
                checks.append(f"✓ 引用{len(result['sources'])}个来源")
            else:
                checks.append("✗ 无引用来源")
            
            # 输出结果
            logger.info(f"\n处理时间: {elapsed:.2f}秒")
            logger.info(f"置信度: {result['confidence']:.2%}")
            logger.info("\n验证结果:")
            for check in checks:
                logger.info(f"  {check}")
            
            logger.info(f"\n答案预览:")
            logger.info(result["answer"][:200] + "..." if len(result["answer"]) > 200 else result["answer"])
            
            # 判断测试是否通过
            if all("✓" in check for check in checks):
                logger.info("\n✅ 测试通过")
                success_count += 1
            else:
                logger.warning("\n⚠️  测试部分失败")
                failed_cases.append(query)
            
        except Exception as e:
            logger.error(f"\n❌ 测试失败: {e}")
            failed_cases.append(query)
    
    # 输出总结
    logger.info(f"\n{'='*60}")
    logger.info("测试总结")
    logger.info(f"{'='*60}")
    logger.info(f"总计: {len(test_cases)} 个测试")
    logger.info(f"成功: {success_count} 个")
    logger.info(f"失败: {len(failed_cases)} 个")
    
    if failed_cases:
        logger.warning("\n失败的测试:")
        for query in failed_cases:
            logger.warning(f"  - {query}")
    
    logger.info(f"\n{'='*60}")
    
    return len(failed_cases) == 0

if __name__ == "__main__":
    success = test_queries()
    sys.exit(0 if success else 1)