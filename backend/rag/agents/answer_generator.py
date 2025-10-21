"""答案生成Agent"""
from typing import List, Dict, Any
from loguru import logger
from ..utils.llm_client import llm_client

class AnswerGeneratorAgent:
    """答案生成Agent - 基于检索结果生成答案"""
    
    def generate(self,
                question: str,
                retrieved_docs: List[Dict[str, Any]],
                book_name: str,
                version: str,
                metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成答案
        
        Args:
            question: 用户问题
            retrieved_docs: 检索到的文档列表
            book_name: 书名
            version: 版本号
            metadata: 书籍元数据
            
        Returns:
            {
                "answer": str,  # 生成的答案
                "sources": list,  # 引用来源
                "confidence": float  # 置信度
            }
        """
        logger.info(f"生成答案: 问题={question}, 文档数={len(retrieved_docs)}")
        
        if not retrieved_docs:
            return {
                "answer": f"抱歉，在《{book_name}》第{version}版中没有找到与您问题相关的内容。",
                "sources": [],
                "confidence": 0.0
            }
        
        # 构建上下文
        context = self._build_context(retrieved_docs)
        
        # 构建提示词
        system_prompt = """你是一个专业的医学教材助手。
任务：基于提供的教材内容回答用户的问题。

要求：
1. 仅使用提供的参考内容回答，不要添加教材中没有的信息
2. 答案要准确、专业、结构清晰
3. 如果参考内容不足以完整回答问题，要明确指出
4. 使用markdown格式，适当使用标题、列表等
5. 回答末尾必须注明具体来源（章节和页码）
"""
        
        prompt = f"""请基于以下来自《{book_name}》第{version}版的内容回答问题。

**书籍信息：**
- 书名：{book_name}
- 版本：第{version}版
- ISBN：{metadata.get('isbn', 'N/A')}
- 出版社：{metadata.get('publisher', 'N/A')}
- 出版年份：{metadata.get('publish_year', 'N/A')}

**用户问题：**
{question}

**参考内容：**
{context}

**回答要求：**
1. 直接回答问题，不要重复问题
2. 内容要专业准确，逻辑清晰
3. 如果有多个要点，使用列表展示
4. 回答末尾用单独一段标注来源，格式：
   > **来源：《{book_name}》第{version}版，第X章，第Y-Z页**
"""
        
        try:
            answer = llm_client.invoke(prompt, system_prompt)
            
            # 提取引用来源
            sources = self._extract_sources(retrieved_docs)
            
            # 计算置信度（基于检索分数）
            confidence = self._calculate_confidence(retrieved_docs)
            
            result = {
                "answer": answer.strip(),
                "sources": sources,
                "confidence": confidence
            }
            
            logger.info(f"✓ 答案生成完成，置信度: {confidence:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"答案生成失败: {e}")
            return {
                "answer": "抱歉，生成答案时出现错误，请稍后重试。",
                "sources": [],
                "confidence": 0.0
            }
    
    def _build_context(self, docs: List[Dict[str, Any]]) -> str:
        """构建上下文"""
        context_parts = []
        
        for i, doc in enumerate(docs, 1):
            metadata = doc["metadata"]
            content = doc["content"]
            score = doc.get("score", 0)
            
            chapter = metadata.get("chapter", "未知章节")
            page = metadata.get("page", "未知页码")
            
            context_part = f"""
[文档 {i}] - 相似度: {score:.4f}
来源：{chapter}，第{page}页
内容：
{content}
"""
            context_parts.append(context_part)
        
        return "\n".join(context_parts)
    
    def _extract_sources(self, docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """提取引用来源"""
        sources = []
        seen_pages = set()  # 去重
        
        for doc in docs:
            metadata = doc["metadata"]
            chapter = metadata.get("chapter", "")
            page = metadata.get("page", "")
            
            # 避免重复引用同一页
            page_key = f"{chapter}_{page}"
            if page_key in seen_pages:
                continue
            
            seen_pages.add(page_key)
            
            source = {
                "chapter": chapter,
                "page": page,
                "score": doc.get("score", 0)
            }
            sources.append(source)
        
        return sources
    
    def _calculate_confidence(self, docs: List[Dict[str, Any]]) -> float:
        """
        计算置信度
        基于检索分数和文档数量
        """
        if not docs:
            return 0.0
        
        # 计算平均相似度分数
        avg_score = sum(doc.get("score", 0) for doc in docs) / len(docs)
        
        # 文档数量因子（有足够文档会提升置信度）
        doc_count_factor = min(len(docs) / 3, 1.0)  # 3个文档为最优
        
        # 综合置信度
        confidence = (avg_score * 0.7 + doc_count_factor * 0.3)
        
        return round(confidence, 2)
    
    def generate_summary(self,
                        book_name: str,
                        version: str,
                        retrieved_docs: List[Dict[str, Any]]) -> str:
        """
        生成内容摘要（可选功能）
        
        Args:
            book_name: 书名
            version: 版本号
            retrieved_docs: 检索到的文档
            
        Returns:
            摘要文本
        """
        if not retrieved_docs:
            return "未找到相关内容"
        
        # 提取所有文档内容
        all_content = "\n\n".join([doc["content"] for doc in retrieved_docs])
        
        prompt = f"""请为以下来自《{book_name}》第{version}版的内容生成一个简洁的摘要（200字以内）：

{all_content}

摘要要求：
- 提炼核心要点
- 保持专业性
- 简洁明了
"""
        
        try:
            summary = llm_client.invoke(prompt)
            return summary.strip()
        except Exception as e:
            logger.error(f"摘要生成失败: {e}")
            return "摘要生成失败"

# 测试代码
if __name__ == "__main__":
    agent = AnswerGeneratorAgent()
    
    # 模拟检索结果
    mock_docs = [
        {
            "content": "队列研究（cohort study）是一种前瞻性研究方法，研究者选定暴露和非暴露人群，随访观察一定时间后比较两组的发病率差异。",
            "metadata": {
                "book_name": "流行病学",
                "version": "7",
                "chapter": "第3章 研究设计",
                "page": 45
            },
            "score": 0.92
        },
        {
            "content": "队列研究的主要优点包括：1）可以直接计算发病率和相对危险度；2）时间顺序明确，因果推断能力强；3）可同时观察多种结局。",
            "metadata": {
                "book_name": "流行病学",
                "version": "7",
                "chapter": "第3章 研究设计",
                "page": 46
            },
            "score": 0.88
        }
    ]
    
    result = agent.generate(
        question="什么是队列研究",
        retrieved_docs=mock_docs,
        book_name="流行病学",
        version="7",
        metadata={"isbn": "978-7-117-15677-5", "publisher": "人民卫生出版社"}
    )
    
    print("生成的答案：")
    print(result["answer"])
    print(f"\n置信度: {result['confidence']}")
    print(f"引用来源: {len(result['sources'])} 处")