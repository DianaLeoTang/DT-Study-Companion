"""
查询问答API路由
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from loguru import logger

router = APIRouter()

class QueryRequest(BaseModel):
    """查询请求模型"""
    question: str
    collection_name: Optional[str] = None
    use_scores: bool = False
    top_k: Optional[int] = None

class QueryResponse(BaseModel):
    """查询响应模型"""
    question: str
    answer: str
    context_documents: List[Dict[str, Any]]
    context_count: int
    collection_name: str

@router.post("/ask", response_model=QueryResponse)
async def ask_question(request: QueryRequest):
    """智能问答接口"""
    try:
        logger.info(f"收到查询: {request.question}")
        
        # 导入RAG服务
        import sys
        from pathlib import Path
        project_root = Path(__file__).parent.parent.parent.parent
        sys.path.insert(0, str(project_root))
        
        try:
            from src.agents.rag_agent import RAGAgent
            from src.preprocessing.vectorstore_builder import VectorStoreBuilder
            
            # 获取向量数据库
            builder = VectorStoreBuilder()
            collection_name = request.collection_name or "docx_卫生统计学第八版"
            vectorstore = builder.get_vectorstore(collection_name)
            
            if vectorstore:
                # 创建RAG代理
                rag_agent = RAGAgent(vectorstore, collection_name)
                
                # 设置检索参数
                if request.top_k:
                    rag_agent.retrieval_top_k = request.top_k
                
                # 执行查询
                result = rag_agent.ask(
                    query=request.question,
                    use_scores=request.use_scores
                )
                
                return QueryResponse(
                    question=request.question,
                    answer=result["answer"],
                    context_documents=result["context_documents"],
                    context_count=result["context_count"],
                    collection_name=collection_name
                )
            else:
                return QueryResponse(
                    question=request.question,
                    answer="抱歉，没有找到相关的文档数据。请先处理文档。",
                    context_documents=[],
                    context_count=0,
                    collection_name=collection_name
                )
                
        except Exception as rag_error:
            logger.error(f"RAG服务错误: {rag_error}")
            return QueryResponse(
                question=request.question,
                answer=f"RAG服务暂时不可用: {str(rag_error)}",
                context_documents=[],
                context_count=0,
                collection_name=request.collection_name or "default"
            )
        
    except Exception as e:
        logger.error(f"查询处理失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/collections")
async def list_collections():
    """获取可用的文档集合"""
    try:
        # 这里应该从向量数据库获取collections
        return {
            "collections": [
                {
                    "name": "docx_卫生统计学第八版",
                    "document_count": 150,
                    "status": "active"
                },
                {
                    "name": "docx_流行病学第九版吕筠", 
                    "document_count": 200,
                    "status": "active"
                }
            ]
        }
    except Exception as e:
        logger.error(f"获取collections失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
