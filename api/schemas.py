'''
Author: Diana Tang
'''
"""API数据模型"""
from pydantic import BaseModel, Field
from typing import List, Optional

class QueryRequest(BaseModel):
    """查询请求"""
    query: str = Field(..., description="用户查询", example="流行病学第7版，什么是队列研究？")
    top_k: Optional[int] = Field(5, description="返回文档数量", ge=1, le=20)

class Source(BaseModel):
    """引用来源"""
    chapter: str = Field(..., description="章节")
    page: int = Field(..., description="页码")
    score: float = Field(..., description="相似度分数")

class QueryResponse(BaseModel):
    """查询响应"""
    answer: str = Field(..., description="生成的答案")
    sources: List[Source] = Field(default_factory=list, description="引用来源")
    confidence: float = Field(..., description="置信度", ge=0, le=1)
    book_name: str = Field(..., description="书名")
    version: str = Field(..., description="版本号")
    question: str = Field(..., description="提炼后的问题")

class BookInfo(BaseModel):
    """书籍信息"""
    id: str
    name: str
    versions: List[str]

class SystemInfo(BaseModel):
    """系统信息"""
    total_books: int
    total_collections: int
    available_books: List[BookInfo]
    embedding_model: str
    llm_model: str

class HealthCheck(BaseModel):
    """健康检查"""
    status: str
    message: str