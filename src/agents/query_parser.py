"""查询解析Agent"""
from typing import Dict, Any
from loguru import logger
from ..utils.llm_client import llm_client
import re

class QueryParserAgent:
    """查询解析Agent - 从用户查询中提取书名、版本号、问题"""
    
    def __init__(self):
        self.llm_client = llm_client
    
    def parse(self, query: str) -> Dict[str, Any]:
        """
        解析用户查询
        
        Args:
            query: 用户原始查询
            
        Returns:
            {
                "book_name": str,      # 书名
                "version": str,        # 版本号
                "question": str,       # 提炼后的问题
                "confidence": float    # 解析置信度
            }
        """
        logger.info(f"解析查询: {query}")
        
        try:
            # 构建解析提示词
            system_prompt = """你是一个专业的查询解析助手。
任务：从用户查询中准确提取书名、版本号和问题。

要求：
1. 书名识别要准确，支持常见医学教材名称
2. 版本号要精确提取（如"第7版"、"第8版"等）
3. 如果没有明确版本，返回空字符串
4. 问题要简洁明了，去除冗余信息
5. 返回JSON格式结果

常见医学教材：
- 流行病学
- 生理学  
- 病理学
- 解剖学
- 药理学
- 内科学
- 外科学
- 妇产科学
- 儿科学
- 神经病学
- 精神病学
- 传染病学
- 医学统计学
- 医学伦理学
"""
            
            prompt = f"""请解析以下用户查询，提取书名、版本号和问题：

用户查询：{query}

请返回JSON格式：
{{
    "book_name": "书名",
    "version": "版本号（如第7版，没有则返回空字符串）",
    "question": "提炼后的问题",
    "confidence": 0.95
}}

注意：
- 书名要准确匹配常见医学教材
- 版本号格式要统一（如"7"、"8"等数字）
- 问题要简洁，去除书名和版本信息
- confidence是解析的置信度（0-1之间）
"""
            
            # 调用LLM解析
            response = self.llm_client.invoke(prompt, system_prompt)
            
            # 尝试从响应中提取JSON
            result = self._extract_json_from_response(response)
            
            # 验证和清理结果
            result = self._validate_and_clean_result(result, query)
            
            logger.info(f"✓ 解析完成: 书名={result['book_name']}, 版本={result['version']}, 问题={result['question']}")
            return result
            
        except Exception as e:
            logger.error(f"✗ 查询解析失败: {e}")
            # 返回默认结果
            return {
                "book_name": "",
                "version": "",
                "question": query,
                "confidence": 0.0
            }
    
    def _extract_json_from_response(self, response: str) -> Dict[str, Any]:
        """从LLM响应中提取JSON"""
        import json
        
        # 尝试直接解析
        try:
            return json.loads(response)
        except:
            pass
        
        # 尝试提取JSON块
        json_pattern = r'\{[^{}]*"book_name"[^{}]*\}'
        matches = re.findall(json_pattern, response, re.DOTALL)
        
        for match in matches:
            try:
                return json.loads(match)
            except:
                continue
        
        # 如果都失败了，尝试手动解析
        return self._manual_parse(response)
    
    def _manual_parse(self, response: str) -> Dict[str, Any]:
        """手动解析响应"""
        result = {
            "book_name": "",
            "version": "",
            "question": "",
            "confidence": 0.5
        }
        
        # 提取书名
        book_patterns = [
            r'"book_name":\s*"([^"]*)"',
            r'书名[：:]\s*([^\n,，。]+)',
            r'《([^》]+)》'
        ]
        
        for pattern in book_patterns:
            match = re.search(pattern, response)
            if match:
                result["book_name"] = match.group(1).strip()
                break
        
        # 提取版本号
        version_patterns = [
            r'"version":\s*"([^"]*)"',
            r'版本[：:]\s*([^\n,，。]+)',
            r'第(\d+)版'
        ]
        
        for pattern in version_patterns:
            match = re.search(pattern, response)
            if match:
                result["version"] = match.group(1).strip()
                break
        
        # 提取问题
        question_patterns = [
            r'"question":\s*"([^"]*)"',
            r'问题[：:]\s*([^\n]+)'
        ]
        
        for pattern in question_patterns:
            match = re.search(pattern, response)
            if match:
                result["question"] = match.group(1).strip()
                break
        
        return result
    
    def _validate_and_clean_result(self, result: Dict[str, Any], original_query: str) -> Dict[str, Any]:
        """验证和清理解析结果"""
        # 确保必要字段存在
        if "book_name" not in result:
            result["book_name"] = ""
        if "version" not in result:
            result["version"] = ""
        if "question" not in result:
            result["question"] = original_query
        if "confidence" not in result:
            result["confidence"] = 0.5
        
        # 清理书名
        book_name = result["book_name"].strip()
        if book_name:
            # 移除书名号
            book_name = re.sub(r'《|》', '', book_name)
            # 移除版本信息
            book_name = re.sub(r'第\d+版', '', book_name)
            result["book_name"] = book_name.strip()
        
        # 清理版本号
        version = result["version"].strip()
        if version:
            # 提取数字
            version_match = re.search(r'(\d+)', version)
            if version_match:
                result["version"] = version_match.group(1)
            else:
                result["version"] = ""
        
        # 清理问题
        question = result["question"].strip()
        if not question:
            result["question"] = original_query
        
        # 确保置信度在合理范围内
        confidence = result.get("confidence", 0.5)
        if not isinstance(confidence, (int, float)) or confidence < 0 or confidence > 1:
            result["confidence"] = 0.5
        
        return result

# 测试代码
if __name__ == "__main__":
    agent = QueryParserAgent()
    
    test_queries = [
        "流行病学第7版，什么是队列研究？",
        "生理学第9版中关于心脏的内容",
        "病理学，肿瘤的发病机制是什么？",
        "什么是高血压？"
    ]
    
    for query in test_queries:
        result = agent.parse(query)
        print(f"\n查询: {query}")
        print(f"书名: {result['book_name']}")
        print(f"版本: {result['version']}")
        print(f"问题: {result['question']}")
        print(f"置信度: {result['confidence']}")
