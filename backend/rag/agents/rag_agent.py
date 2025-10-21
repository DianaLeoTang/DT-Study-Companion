"""RAG问答代理"""
from typing import List, Dict, Any, Optional
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from loguru import logger
from ..utils.config import Config
from ..utils.llm_client import LLMClient

class RAGAgent:
    """RAG问答代理"""
    
    def __init__(self, vectorstore: Chroma = None, collection_name: str = None):
        self.vectorstore = vectorstore
        self.collection_name = collection_name
        self.llm_client = LLMClient()
        self.retrieval_top_k = Config.RETRIEVAL_TOP_K
        self.retrieval_score_threshold = Config.RETRIEVAL_SCORE_THRESHOLD
    
    def set_vectorstore(self, vectorstore: Chroma, collection_name: str):
        """设置向量数据库"""
        self.vectorstore = vectorstore
        self.collection_name = collection_name
        logger.info(f"RAG代理已连接到collection: {collection_name}")
    
    def retrieve_documents(self, query: str, top_k: int = None) -> List[Document]:
        """
        检索相关文档
        
        Args:
            query: 查询文本
            top_k: 返回文档数量
            
        Returns:
            相关文档列表
        """
        if not self.vectorstore:
            logger.error("向量数据库未设置")
            return []
        
        if top_k is None:
            top_k = self.retrieval_top_k
        
        try:
            # 使用相似性搜索
            docs = self.vectorstore.similarity_search(
                query, 
                k=top_k
            )
            
            logger.info(f"检索到 {len(docs)} 个相关文档")
            return docs
            
        except Exception as e:
            logger.error(f"文档检索失败: {e}")
            return []
    
    def retrieve_documents_with_scores(self, query: str, top_k: int = None) -> List[tuple]:
        """
        检索相关文档并返回相似度分数
        
        Args:
            query: 查询文本
            top_k: 返回文档数量
            
        Returns:
            (文档, 分数) 元组列表
        """
        if not self.vectorstore:
            logger.error("向量数据库未设置")
            return []
        
        if top_k is None:
            top_k = self.retrieval_top_k
        
        try:
            # 使用相似性搜索并返回分数
            docs_with_scores = self.vectorstore.similarity_search_with_score(
                query, 
                k=top_k
            )
            
            # 过滤低分文档
            filtered_docs = [
                (doc, score) for doc, score in docs_with_scores
                if score >= self.retrieval_score_threshold
            ]
            
            logger.info(f"检索到 {len(filtered_docs)} 个相关文档 (阈值: {self.retrieval_score_threshold})")
            return filtered_docs
            
        except Exception as e:
            logger.error(f"文档检索失败: {e}")
            return []
    
    def generate_answer(self, query: str, context_docs: List[Document]) -> str:
        """
        基于检索到的文档生成答案
        
        Args:
            query: 用户问题
            context_docs: 检索到的相关文档
            
        Returns:
            生成的答案
        """
        if not context_docs:
            return "抱歉，我没有找到相关的信息来回答您的问题。"
        
        # 构建上下文
        context = self._build_context(context_docs)
        
        # 构建提示词
        prompt = self._build_prompt(query, context)
        
        try:
            # 调用LLM生成答案
            answer = self.llm_client.generate(prompt)
            return answer
            
        except Exception as e:
            logger.error(f"答案生成失败: {e}")
            return f"抱歉，生成答案时出现错误: {str(e)}"
    
    def ask(self, query: str, use_scores: bool = False) -> Dict[str, Any]:
        """
        完整的问答流程
        
        Args:
            query: 用户问题
            use_scores: 是否使用相似度分数过滤
            
        Returns:
            包含答案和相关文档的字典
        """
        logger.info(f"处理问题: {query}")
        
        # 检索相关文档
        if use_scores:
            docs_with_scores = self.retrieve_documents_with_scores(query)
            context_docs = [doc for doc, score in docs_with_scores]
            scores = [score for doc, score in docs_with_scores]
        else:
            context_docs = self.retrieve_documents(query)
            scores = []
        
        # 生成答案
        answer = self.generate_answer(query, context_docs)
        
        # 构建结果
        result = {
            "query": query,
            "answer": answer,
            "context_documents": [
                {
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": scores[i] if scores else None
                }
                for i, doc in enumerate(context_docs)
            ],
            "context_count": len(context_docs)
        }
        
        logger.info(f"问答完成，使用了 {len(context_docs)} 个相关文档")
        return result
    
    def _build_context(self, docs: List[Document]) -> str:
        """构建上下文文本"""
        context_parts = []
        
        for i, doc in enumerate(docs, 1):
            # 添加文档来源信息
            metadata = doc.metadata
            source_info = []
            
            if "book_name" in metadata:
                source_info.append(f"书籍: {metadata['book_name']}")
            if "chapter" in metadata:
                source_info.append(f"章节: {metadata['chapter']}")
            if "page" in metadata:
                source_info.append(f"页码: {metadata['page']}")
            elif "paragraph" in metadata:
                source_info.append(f"段落: {metadata['paragraph']}")
            
            source_text = f"【文档{i}】" + (f" ({', '.join(source_info)})" if source_info else "")
            
            context_parts.append(f"{source_text}\n{doc.page_content}")
        
        return "\n\n".join(context_parts)
    
    def _build_prompt(self, query: str, context: str) -> str:
        """构建提示词"""
        prompt = f"""你是一个专业的医学知识助手，请基于以下上下文信息回答用户的问题。

上下文信息：
{context}

用户问题：{query}

请根据上下文信息提供准确、详细的回答。如果上下文中没有足够的信息来回答问题，请明确说明。

回答要求：
1. 基于提供的上下文信息进行回答
2. 回答要准确、专业、易懂
3. 如果涉及具体数据或概念，请引用来源
4. 如果上下文信息不足，请诚实说明
5. 回答要结构清晰，重点突出

回答："""
        
        return prompt
    
    def get_collection_info(self) -> Dict[str, Any]:
        """获取collection信息"""
        if not self.vectorstore:
            return {"error": "向量数据库未设置"}
        
        try:
            # 获取collection统计信息
            collection = self.vectorstore._collection
            count = collection.count()
            
            return {
                "collection_name": self.collection_name,
                "document_count": count,
                "status": "connected"
            }
            
        except Exception as e:
            return {
                "collection_name": self.collection_name,
                "error": str(e),
                "status": "error"
            }

# 测试代码
if __name__ == "__main__":
    from src.preprocessing.vectorstore_builder import VectorStoreBuilder
    
    # 测试RAG代理
    print("测试RAG代理...")
    
    # 创建测试数据
    test_chunks = [
        {
            "content": "卫生统计学是研究卫生领域中数据的收集、整理、分析和解释的科学。",
            "metadata": {
                "book_name": "卫生统计学",
                "chapter": "第一章",
                "page": 1,
                "book_id": "test",
                "version": "1"
            }
        },
        {
            "content": "流行病学是研究人群中疾病和健康状态的分布及其决定因素的科学。",
            "metadata": {
                "book_name": "流行病学",
                "chapter": "第一章",
                "page": 1,
                "book_id": "test",
                "version": "1"
            }
        }
    ]
    
    # 构建向量数据库
    builder = VectorStoreBuilder()
    vectorstore = builder.build_collection("test_rag", test_chunks, force_rebuild=True)
    
    # 创建RAG代理
    rag_agent = RAGAgent(vectorstore, "test_rag")
    
    # 测试问答
    result = rag_agent.ask("什么是卫生统计学？")
    print(f"问题: {result['query']}")
    print(f"答案: {result['answer']}")
    print(f"使用了 {result['context_count']} 个相关文档")
