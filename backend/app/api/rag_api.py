"""RAG API接口"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn
from loguru import logger

from src.preprocessing.vectorstore_builder import VectorStoreBuilder
from src.agents.rag_agent import RAGAgent
from src.utils.config import Config

app = FastAPI(
    title="DT Study Companion RAG API",
    description="基于DOCX文档的RAG问答系统API",
    version="1.0.0"
)

# 全局变量存储RAG代理
rag_agents: Dict[str, RAGAgent] = {}

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

class CollectionInfo(BaseModel):
    """Collection信息模型"""
    collection_name: str
    document_count: int
    status: str

def get_rag_agent(collection_name: str) -> RAGAgent:
    """获取RAG代理"""
    if collection_name not in rag_agents:
        # 尝试加载向量数据库
        builder = VectorStoreBuilder()
        vectorstore = builder.get_vectorstore(collection_name)
        
        if not vectorstore:
            raise HTTPException(
                status_code=404, 
                detail=f"Collection '{collection_name}' 不存在"
            )
        
        # 创建RAG代理
        rag_agent = RAGAgent(vectorstore, collection_name)
        rag_agents[collection_name] = rag_agent
    
    return rag_agents[collection_name]

@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info("RAG API 启动中...")
    
    # 验证配置
    if not Config.validate_config():
        logger.error("配置验证失败")
        raise Exception("配置验证失败")
    
    # 预加载可用的collections
    builder = VectorStoreBuilder()
    collections = builder.list_collections()
    
    logger.info(f"发现 {len(collections)} 个可用的collections:")
    for collection in collections:
        logger.info(f"  - {collection}")
    
    logger.info("RAG API 启动完成")

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "DT Study Companion RAG API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/collections", response_model=List[CollectionInfo])
async def list_collections():
    """列出所有可用的collections"""
    builder = VectorStoreBuilder()
    collections = builder.list_collections()
    
    collection_infos = []
    for collection_name in collections:
        try:
            rag_agent = get_rag_agent(collection_name)
            info = rag_agent.get_collection_info()
            collection_infos.append(CollectionInfo(**info))
        except Exception as e:
            logger.warning(f"无法获取collection信息 {collection_name}: {e}")
            collection_infos.append(CollectionInfo(
                collection_name=collection_name,
                document_count=0,
                status="error"
            ))
    
    return collection_infos

@app.get("/collections/{collection_name}", response_model=CollectionInfo)
async def get_collection_info(collection_name: str):
    """获取特定collection的信息"""
    try:
        rag_agent = get_rag_agent(collection_name)
        info = rag_agent.get_collection_info()
        return CollectionInfo(**info)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """查询文档"""
    try:
        # 如果没有指定collection，使用第一个可用的
        if not request.collection_name:
            builder = VectorStoreBuilder()
            collections = builder.list_collections()
            if not collections:
                raise HTTPException(
                    status_code=404, 
                    detail="没有可用的collections"
                )
            request.collection_name = collections[0]
        
        # 获取RAG代理
        rag_agent = get_rag_agent(request.collection_name)
        
        # 设置检索参数
        if request.top_k:
            rag_agent.retrieval_top_k = request.top_k
        
        # 执行查询
        result = rag_agent.ask(
            query=request.question,
            use_scores=request.use_scores
        )
        
        # 添加collection名称到响应
        result["collection_name"] = request.collection_name
        
        return QueryResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"查询失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query/{collection_name}", response_model=QueryResponse)
async def query_specific_collection(collection_name: str, request: QueryRequest):
    """查询特定collection"""
    request.collection_name = collection_name
    return await query_documents(request)

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "collections_count": len(rag_agents),
        "available_collections": list(rag_agents.keys())
    }

if __name__ == "__main__":
    import os
    # 从环境变量获取配置，如果没有则使用默认值
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    
    print(f"🚀 启动RAG API服务器...")
    print(f"🌐 地址: http://{host}:{port}")
    print(f"📖 API文档: http://{host}:{port}/docs")
    
    uvicorn.run(
        "rag_api:app",
        host=host,
        port=port,
        reload=False,  # 关闭热重载避免问题
        log_level="info"
    )
