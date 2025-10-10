"""向量数据库构建模块"""
from typing import List, Dict, Any, Optional
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
from loguru import logger
from ..utils.config import Config
import os

class VectorStoreBuilder:
    """向量数据库构建器"""
    
    def __init__(self):
        self.embeddings = self._init_embeddings()
        self.db_type = Config.VECTOR_DB
        self.persist_dir = Config.CHROMA_PATH
    
    def _init_embeddings(self):
        """初始化Embedding模型"""
        logger.info(f"加载Embedding模型: {Config.EMBEDDING_MODEL}")
        
        model_kwargs = {"device": Config.EMBEDDING_DEVICE}
        encode_kwargs = {"normalize_embeddings": True}
        
        embeddings = HuggingFaceEmbeddings(
            model_name=Config.EMBEDDING_MODEL,
            model_kwargs=model_kwargs,
            encode_kwargs=encode_kwargs
        )
        
        logger.info("Embedding模型加载完成")
        return embeddings
    
    def build_collection(self, 
                        collection_name: str,
                        chunks: List[Dict[str, Any]],
                        force_rebuild: bool = False) -> Chroma:
        """
        构建单个collection
        
        Args:
            collection_name: collection名称
            chunks: 文本块列表
            force_rebuild: 是否强制重建
            
        Returns:
            Chroma向量数据库实例
        """
        logger.info(f"构建collection: {collection_name}")
        
        collection_path = os.path.join(self.persist_dir, collection_name)
        
        # 检查是否已存在
        if os.path.exists(collection_path) and not force_rebuild:
            logger.info(f"Collection已存在，跳过: {collection_name}")
            return Chroma(
                collection_name=collection_name,
                embedding_function=self.embeddings,
                persist_directory=self.persist_dir
            )
        
        # 转换为Document对象
        documents = []
        for chunk in chunks:
            doc = Document(
                page_content=chunk["content"],
                metadata=chunk["metadata"]
            )
            documents.append(doc)
        
        logger.info(f"准备插入 {len(documents)} 个文档")
        
        # 创建向量数据库
        try:
            vectorstore = Chroma.from_documents(
                documents=documents,
                embedding=self.embeddings,
                collection_name=collection_name,
                persist_directory=self.persist_dir
            )
            
            logger.info(f"✓ Collection构建完成: {collection_name}")
            return vectorstore
            
        except Exception as e:
            logger.error(f"✗ Collection构建失败: {e}")
            raise
    
    def build_all_collections(self, 
                             all_chunks: Dict[str, List[Dict[str, Any]]],
                             force_rebuild: bool = False):
        """
        批量构建所有collections
        
        Args:
            all_chunks: {collection_name: [chunks]}
            force_rebuild: 是否强制重建
        """
        logger.info(f"开始构建 {len(all_chunks)} 个collections")
        
        success_count = 0
        failed_collections = []
        
        for collection_name, chunks in all_chunks.items():
            try:
                self.build_collection(
                    collection_name=collection_name,
                    chunks=chunks,
                    force_rebuild=force_rebuild
                )
                success_count += 1
            except Exception as e:
                logger.error(f"Collection构建失败: {collection_name}, 错误: {e}")
                failed_collections.append(collection_name)
        
        logger.info(f"构建完成: 成功 {success_count}/{len(all_chunks)}")
        if failed_collections:
            logger.warning(f"失败的collections: {', '.join(failed_collections)}")
    
    def get_vectorstore(self, collection_name: str) -> Optional[Chroma]:
        """
        获取已存在的vectorstore
        
        Args:
            collection_name: collection名称
            
        Returns:
            Chroma实例，如果不存在返回None
        """
        collection_path = os.path.join(self.persist_dir, collection_name)
        
        if not os.path.exists(collection_path):
            logger.warning(f"Collection不存在: {collection_name}")
            return None
        
        try:
            vectorstore = Chroma(
                collection_name=collection_name,
                embedding_function=self.embeddings,
                persist_directory=self.persist_dir
            )
            return vectorstore
        except Exception as e:
            logger.error(f"加载vectorstore失败: {e}")
            return None
    
    def list_collections(self) -> List[str]:
        """列出所有可用的collections"""
        if not os.path.exists(self.persist_dir):
            return []
        
        collections = [
            d for d in os.listdir(self.persist_dir)
            if os.path.isdir(os.path.join(self.persist_dir, d))
        ]
        
        return collections
    
    def delete_collection(self, collection_name: str):
        """删除指定collection"""
        import shutil
        
        collection_path = os.path.join(self.persist_dir, collection_name)
        if os.path.exists(collection_path):
            shutil.rmtree(collection_path)
            logger.info(f"已删除collection: {collection_name}")
        else:
            logger.warning(f"Collection不存在: {collection_name}")

# 测试代码
if __name__ == "__main__":
    builder = VectorStoreBuilder()
    
    # 测试创建collection
    test_chunks = [
        {
            "content": "这是测试文本1",
            "metadata": {
                "book_name": "测试书籍",
                "version": "1",
                "page": 1
            }
        }
    ]
    
    builder.build_collection("test_collection", test_chunks, force_rebuild=True)
    print("Collections:", builder.list_collections())