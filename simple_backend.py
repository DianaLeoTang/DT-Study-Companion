#!/usr/bin/env python3
"""
简单的后端API - 直接修复问题
"""
import sys
import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn
from loguru import logger

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 创建FastAPI应用
app = FastAPI(
    title="DT Study Companion API",
    description="基于RAG的智能问答系统",
    version="2.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据模型
class QueryRequest(BaseModel):
    question: str
    collection_name: Optional[str] = None
    use_scores: bool = False
    top_k: Optional[int] = None

class QueryResponse(BaseModel):
    question: str
    answer: str
    context_documents: List[Dict[str, Any]]
    context_count: int
    collection_name: str

# API路由
@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "DT Study Companion API",
        "version": "2.0.0",
        "status": "running"
    }

@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": "DT Study Companion API",
        "version": "2.0.0"
    }

@app.get("/api/queries/collections")
async def list_collections():
    """获取文档集合列表"""
    try:
        import chromadb
        client = chromadb.PersistentClient(path='./database/chroma_db')
        collections = client.list_collections()
        
        result = []
        for coll in collections:
            result.append({
                "name": coll.name,
                "document_count": coll.count(),
                "status": "active"
            })
        
        return {"collections": result}
    except Exception as e:
        logger.error(f"获取collections失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/queries/ask", response_model=QueryResponse)
async def ask_question(request: QueryRequest):
    """智能问答接口"""
    try:
        logger.info(f"收到查询: {request.question}")
        
        # 直接使用ChromaDB查询
        try:
            import chromadb
            
            # 连接ChromaDB
            client = chromadb.PersistentClient(path='./database/chroma_db')
            
            # 选择collection
            collection_name = request.collection_name or "test_collection"
            try:
                collection = client.get_collection(collection_name)
            except:
                # 如果指定的collection不存在，使用第一个
                collections = client.list_collections()
                if not collections:
                    return QueryResponse(
                        question=request.question,
                        answer="抱歉，系统中没有任何文档数据。",
                        context_documents=[],
                        context_count=0,
                        collection_name="无"
                    )
                collection = collections[0]
                collection_name = collection.name
            
            # 使用ChromaDB的语义查询
            results = collection.query(
                query_texts=[request.question],
                n_results=request.top_k or 5
            )
            
            # 构建上下文
            context_docs = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    metadata = results['metadatas'][0][i] if results['metadatas'] else {}
                    context_docs.append({
                        "content": doc,
                        "metadata": metadata,
                        "score": results['distances'][0][i] if results['distances'] else 0
                    })
            
            # 生成答案（简单拼接上下文）
            if context_docs:
                context_text = "\n\n".join([doc["content"][:200] for doc in context_docs[:3]])
                answer = f"根据文档内容：\n\n{context_text}\n\n（注意：这是基于文档检索的结果，完整的RAG功能需要配置LLM）"
            else:
                answer = "抱歉，没有找到相关的文档内容。"
            
            return QueryResponse(
                question=request.question,
                answer=answer,
                context_documents=context_docs,
                context_count=len(context_docs),
                collection_name=collection_name
            )
                
        except Exception as rag_error:
            logger.error(f"查询错误: {rag_error}")
            import traceback
            logger.error(traceback.format_exc())
            return QueryResponse(
                question=request.question,
                answer=f"查询出错: {str(rag_error)}",
                context_documents=[],
                context_count=0,
                collection_name=request.collection_name or "default"
            )
        
    except Exception as e:
        logger.error(f"查询处理失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    logger.info("🚀 启动简化后端API...")
    logger.info("🌐 地址: http://localhost:8000")
    logger.info("📖 API文档: http://localhost:8000/docs")
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        reload=False,
        log_level="info"
    )
