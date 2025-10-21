'''
Author: Diana Tang
'''
"""API数据模型"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

# ===== 认证相关模型 =====

class UserLoginRequest(BaseModel):
    """用户登录请求"""
    phone: str = Field(..., description="手机号", example="13800138000")

class UserRegisterRequest(BaseModel):
    """用户注册请求"""
    phone: str = Field(..., description="手机号", example="13800138000")
    nickname: Optional[str] = Field(None, description="昵称", example="小明")

class UserProfile(BaseModel):
    """用户资料"""
    id: str = Field(..., description="用户ID")
    phone: str = Field(..., description="手机号")
    nickname: str = Field(..., description="昵称")
    avatar_url: Optional[str] = Field(None, description="头像URL")

class UserLoginResponse(BaseModel):
    """用户登录响应"""
    token: str = Field(..., description="访问令牌")
    user: UserProfile = Field(..., description="用户信息")

# ===== 查询相关模型 =====

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

# ===== Agent相关模型 =====

class AgentInfo(BaseModel):
    """Agent信息"""
    id: str = Field(..., description="Agent ID")
    name: str = Field(..., description="Agent名称")
    display_name: str = Field(..., description="显示名称")
    description: str = Field(..., description="描述")
    icon: str = Field(..., description="图标")
    config: Dict[str, Any] = Field(default_factory=dict, description="配置信息")

class AgentListResponse(BaseModel):
    """Agent列表响应"""
    agents: List[AgentInfo] = Field(..., description="Agent列表")

# ===== 用户统计模型 =====

class UserStats(BaseModel):
    """用户统计信息"""
    total_queries: int = Field(..., description="总查询次数")
    recent_queries: int = Field(..., description="最近7天查询次数")
    popular_books: List[Dict[str, Any]] = Field(default_factory=list, description="热门书籍")

# ===== 系统信息模型 =====

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