"""检索Agent"""
from typing import List, Dict, Any, Optional
from loguru import logger
from ..preprocessing.vectorstore_builder import VectorStoreBuilder
from ..utils.config import Config

class RetrieverAgent:
    """检索Agent - 从向量数据库中检索相关文档"""
    
    def __init__(self):
        self.vectorstore_builder = VectorStoreBuilder()
        self.top_k = Config.RETRIEVAL_TOP_K
        self.score_threshold = Config.RETRIEVAL_SCORE_THRESHOLD
    
    def retrieve(self, 
                collection_name: str, 
                question: str, 
                version: str = None,
                top_k: int = None,
                score_threshold: float = None) -> List[Dict[str, Any]]:
        """
        检索相关文档
        
        Args:
            collection_name: collection名称
            question: 查询问题
            version: 版本号（用于二次验证）
            top_k: 返回文档数量
            score_threshold: 相似度阈值
            
        Returns:
            检索到的文档列表
        """
        logger.info(f"检索文档: collection={collection_name}, 问题={question}")
        
        # 使用配置的默认值
        if top_k is None:
            top_k = self.top_k
        if score_threshold is None:
            score_threshold = self.score_threshold
        
        try:
            # 获取向量数据库
            vectorstore = self.vectorstore_builder.get_vectorstore(collection_name)
            if not vectorstore:
                logger.warning(f"Collection不存在: {collection_name}")
                return []
            
            # 执行相似度搜索
            docs_with_scores = vectorstore.similarity_search_with_score(
                question, 
                k=top_k
            )
            
            # 处理检索结果
            results = []
            for doc, score in docs_with_scores:
                # 计算相似度分数（ChromaDB返回的是距离，需要转换为相似度）
                similarity_score = 1 / (1 + score)
                
                # 过滤低相似度文档
                if similarity_score < score_threshold:
                    continue
                
                # 二次验证版本号（如果提供了版本）
                if version and doc.metadata.get("version") != version:
                    logger.warning(f"版本不匹配: 期望{version}, 实际{doc.metadata.get('version')}")
                    continue
                
                result = {
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": similarity_score
                }
                results.append(result)
            
            logger.info(f"✓ 检索完成: 找到 {len(results)} 个相关文档")
            
            # 按相似度排序
            results.sort(key=lambda x: x["score"], reverse=True)
            
            return results
            
        except Exception as e:
            logger.error(f"✗ 文档检索失败: {e}")
            return []
    
    def retrieve_with_filters(self,
                             collection_name: str,
                             question: str,
                             filters: Dict[str, Any] = None,
                             top_k: int = None) -> List[Dict[str, Any]]:
        """
        带过滤条件的检索
        
        Args:
            collection_name: collection名称
            question: 查询问题
            filters: 过滤条件
            top_k: 返回文档数量
            
        Returns:
            检索到的文档列表
        """
        logger.info(f"带过滤条件检索: collection={collection_name}, 过滤条件={filters}")
        
        if top_k is None:
            top_k = self.top_k
        
        try:
            # 获取向量数据库
            vectorstore = self.vectorstore_builder.get_vectorstore(collection_name)
            if not vectorstore:
                logger.warning(f"Collection不存在: {collection_name}")
                return []
            
            # 执行带过滤的搜索
            docs_with_scores = vectorstore.similarity_search_with_score(
                question,
                k=top_k,
                filter=filters
            )
            
            # 处理检索结果
            results = []
            for doc, score in docs_with_scores:
                similarity_score = 1 / (1 + score)
                
                result = {
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": similarity_score
                }
                results.append(result)
            
            logger.info(f"✓ 过滤检索完成: 找到 {len(results)} 个相关文档")
            
            # 按相似度排序
            results.sort(key=lambda x: x["score"], reverse=True)
            
            return results
            
        except Exception as e:
            logger.error(f"✗ 过滤检索失败: {e}")
            return []
    
    def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """获取collection信息"""
        try:
            vectorstore = self.vectorstore_builder.get_vectorstore(collection_name)
            if not vectorstore:
                return {"exists": False}
            
            # 获取collection统计信息
            collection = vectorstore._collection
            count = collection.count()
            
            return {
                "exists": True,
                "document_count": count,
                "collection_name": collection_name
            }
            
        except Exception as e:
            logger.error(f"获取collection信息失败: {e}")
            return {"exists": False, "error": str(e)}
    
    def list_available_collections(self) -> List[str]:
        """列出所有可用的collections"""
        return self.vectorstore_builder.list_collections()
    
    def search_by_chapter(self, 
                         collection_name: str, 
                         question: str, 
                         chapter: str,
                         top_k: int = None) -> List[Dict[str, Any]]:
        """
        按章节搜索
        
        Args:
            collection_name: collection名称
            question: 查询问题
            chapter: 章节名称
            top_k: 返回文档数量
            
        Returns:
            检索到的文档列表
        """
        filters = {"chapter": chapter}
        return self.retrieve_with_filters(collection_name, question, filters, top_k)
    
    def search_by_page_range(self,
                           collection_name: str,
                           question: str,
                           start_page: int,
                           end_page: int,
                           top_k: int = None) -> List[Dict[str, Any]]:
        """
        按页码范围搜索
        
        Args:
            collection_name: collection名称
            question: 查询问题
            start_page: 起始页码
            end_page: 结束页码
            top_k: 返回文档数量
            
        Returns:
            检索到的文档列表
        """
        # 注意：这里需要根据实际的元数据结构调整过滤条件
        # 假设页码存储在page字段中
        filters = {
            "page": {"$gte": start_page, "$lte": end_page}
        }
        return self.retrieve_with_filters(collection_name, question, filters, top_k)

# 测试代码
if __name__ == "__main__":
    agent = RetrieverAgent()
    
    # 测试基本检索
    results = agent.retrieve(
        collection_name="epidemiology_v7",
        question="什么是队列研究？",
        top_k=5
    )
    
    print(f"检索到 {len(results)} 个文档:")
    for i, result in enumerate(results, 1):
        print(f"{i}. 相似度: {result['score']:.4f}")
        print(f"   章节: {result['metadata'].get('chapter', 'N/A')}")
        print(f"   页码: {result['metadata'].get('page', 'N/A')}")
        print(f"   内容: {result['content'][:100]}...")
        print()
    
    # 测试collection信息
    info = agent.get_collection_info("epidemiology_v7")
    print(f"Collection信息: {info}")
    
    # 列出所有collections
    collections = agent.list_available_collections()
    print(f"可用collections: {collections}")
