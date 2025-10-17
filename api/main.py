"""
DT-Study-Companion 主API服务
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
import uvicorn
from loguru import logger

# 导入模块
from .database import get_db, init_database
from .models import User
from .auth import get_current_user, security
from .schemas import (
    QueryRequest, QueryResponse, SystemInfo, HealthCheck,
    UserLoginRequest, UserLoginResponse, UserRegisterRequest,
    AgentListResponse, AgentInfo, UserProfile, UserStats
)
from .services.user_service import UserService
from .services.agent_service import AgentService
try:
    from ..src.workflow.agent_graph import TextbookAssistant
except ImportError:
    # 如果导入失败，创建一个简单的占位类
    class TextbookAssistant:
        def __init__(self):
            pass
        def query(self, query):
            return {
                "answer": "系统正在初始化中，请稍后重试",
                "sources": [],
                "confidence": 0.0,
                "book_name": "",
                "version": "",
                "question": query
            }

# 安全方案从auth模块导入

# 全局变量
assistant = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global assistant
    
    # 启动时初始化
    logger.info("正在初始化DT-Study-Companion...")
    
    # 初始化数据库
    init_database()
    
    # 初始化课本助手
    assistant = TextbookAssistant()
    
    logger.info("DT-Study-Companion初始化完成")
    
    yield
    
    # 关闭时清理
    logger.info("DT-Study-Companion正在关闭...")

# 创建FastAPI应用
app = FastAPI(
    title="DT-Study-Companion API",
    description="清瑶书院AI助教 - 为你的公共卫生研学之路提供温度与智慧的陪伴",
    version="1.0.0",
    lifespan=lifespan
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 服务实例
user_service = UserService()
agent_service = AgentService()

# ===== 认证相关接口 =====

@app.post("/auth/register", response_model=UserLoginResponse)
async def register(request: UserRegisterRequest, db: Session = Depends(get_db)):
    """用户注册"""
    try:
        # 创建用户
        user = user_service.create_user(db, request.phone, request.nickname)
        
        # 创建会话
        from .auth import auth_service
        token = auth_service.create_user_session(db, user.id)
        
        return UserLoginResponse(
            token=token,
            user=UserProfile(
                id=user.id,
                phone=user.phone,
                nickname=user.nickname,
                avatar_url=user.avatar_url
            )
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"用户注册失败: {e}")
        raise HTTPException(status_code=500, detail="注册失败")

@app.post("/auth/login", response_model=UserLoginResponse)
async def login(request: UserLoginRequest, db: Session = Depends(get_db)):
    """用户登录"""
    try:
        # 查找用户
        user = user_service.get_user_by_phone(db, request.phone)
        if not user:
            # 自动注册
            user = user_service.create_user(db, request.phone)
        
        # 创建会话
        from .auth import auth_service
        token = auth_service.create_user_session(db, user.id)
        
        return UserLoginResponse(
            token=token,
            user=UserProfile(
                id=user.id,
                phone=user.phone,
                nickname=user.nickname,
                avatar_url=user.avatar_url
            )
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"用户登录失败: {e}")
        raise HTTPException(status_code=500, detail="登录失败")

@app.post("/auth/logout")
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """用户登出"""
    try:
        from .auth import auth_service
        success = auth_service.logout_user(db, credentials.credentials)
        
        if success:
            return {"message": "登出成功"}
        else:
            raise HTTPException(status_code=400, detail="登出失败")
            
    except Exception as e:
        logger.error(f"用户登出失败: {e}")
        raise HTTPException(status_code=500, detail="登出失败")

# ===== 用户相关接口 =====

@app.get("/user/profile", response_model=UserProfile)
async def get_user_profile(
    current_user: User = Depends(get_current_user)
):
    """获取用户资料"""
    return UserProfile(
        id=current_user.id,
        phone=current_user.phone,
        nickname=current_user.nickname,
        avatar_url=current_user.avatar_url
    )

@app.put("/user/profile", response_model=UserProfile)
async def update_user_profile(
    profile: UserProfile,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新用户资料"""
    try:
        updated_user = user_service.update_user_profile(
            db, current_user.id, 
            nickname=profile.nickname,
            avatar_url=profile.avatar_url
        )
        
        if updated_user:
            return UserProfile(
                id=updated_user.id,
                phone=updated_user.phone,
                nickname=updated_user.nickname,
                avatar_url=updated_user.avatar_url
            )
        else:
            raise HTTPException(status_code=404, detail="用户不存在")
            
    except Exception as e:
        logger.error(f"更新用户资料失败: {e}")
        raise HTTPException(status_code=500, detail="更新失败")

@app.get("/user/stats", response_model=UserStats)
async def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户统计信息"""
    try:
        stats = user_service.get_user_stats(db, current_user.id)
        return UserStats(**stats)
        
    except Exception as e:
        logger.error(f"获取用户统计失败: {e}")
        raise HTTPException(status_code=500, detail="获取统计失败")

@app.get("/user/history")
async def get_user_history(
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户查询历史"""
    try:
        history = user_service.get_user_query_history(
            db, current_user.id, limit, offset
        )
        
        return {
            "history": [
                {
                    "id": h.id,
                    "query": h.query,
                    "answer": h.answer,
                    "book_name": h.book_name,
                    "version": h.version,
                    "confidence": h.confidence,
                    "agent_type": h.agent_type,
                    "created_at": h.created_at.isoformat()
                }
                for h in history
            ],
            "total": len(history)
        }
        
    except Exception as e:
        logger.error(f"获取查询历史失败: {e}")
        raise HTTPException(status_code=500, detail="获取历史失败")

# ===== Agent相关接口 =====

@app.get("/agents", response_model=AgentListResponse)
async def get_agents(db: Session = Depends(get_db)):
    """获取所有可用的Agent"""
    try:
        agents = agent_service.get_all_agents(db)
        
        return AgentListResponse(
            agents=[
                AgentInfo(
                    id=agent.id,
                    name=agent.name,
                    display_name=agent.display_name,
                    description=agent.description,
                    icon=agent.icon,
                    config=agent_service.get_agent_config(agent)
                )
                for agent in agents
            ]
        )
        
    except Exception as e:
        logger.error(f"获取Agent列表失败: {e}")
        raise HTTPException(status_code=500, detail="获取Agent列表失败")

# ===== 查询相关接口 =====

@app.post("/query", response_model=QueryResponse)
async def query(
    request: QueryRequest,
    agent_name: str = "epidemiology",
    version: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """执行查询"""
    try:
        if not assistant:
            raise HTTPException(status_code=500, detail="系统未初始化")
        
        # 构建带版本的查询
        query_text = request.query
        if version:
            # 如果指定了版本，在查询中明确版本信息
            if agent_name == "epidemiology":
                if version == "8":
                    query_text = f"流行病学第8版，{request.query}"
                elif version == "9":
                    query_text = f"流行病学第9版，{request.query}"
            elif agent_name == "health_statistics":
                if version == "8":
                    query_text = f"卫生统计学第8版，{request.query}"
                elif version == "wangyan_v2":
                    query_text = f"卫生统计学王燕第二版，{request.query}"
            elif agent_name == "social_medicine":
                if version == "2":
                    query_text = f"社会医学第二版，{request.query}"
                elif version == "5":
                    query_text = f"社会医学第五版，{request.query}"
        
        # 执行查询
        result = assistant.query(query_text)
        
        # 保存查询历史
        user_service.add_query_history(
            db=db,
            user_id=current_user.id,
            query=request.query,
            answer=result["answer"],
            book_name=result["book_name"],
            version=result["version"],
            confidence=str(result["confidence"]),
            agent_type=f"{agent_name}_{version}" if version else agent_name
        )
        
        return QueryResponse(
            answer=result["answer"],
            sources=result["sources"],
            confidence=result["confidence"],
            book_name=result["book_name"],
            version=result["version"],
            question=result["question"]
        )
        
    except Exception as e:
        logger.error(f"查询执行失败: {e}")
        raise HTTPException(status_code=500, detail="查询失败")

# ===== 系统信息接口 =====

@app.get("/system/info", response_model=SystemInfo)
async def get_system_info():
    """获取系统信息"""
    try:
        try:
            from ..src.preprocessing.vectorstore_builder import VectorStoreBuilder
            builder = VectorStoreBuilder()
            collections = builder.list_collections()
            total_books = len(set([c.split('_v')[0] for c in collections]))
            total_collections = len(collections)
        except ImportError:
            # 如果导入失败，使用默认值
            total_books = 0
            total_collections = 0
        
        return SystemInfo(
            total_books=total_books,
            total_collections=total_collections,
            available_books=[],  # 这里可以添加具体的书籍信息
            embedding_model="BAAI/bge-large-zh-v1.5",
            llm_model="gpt-4-turbo-preview"
        )
        
    except Exception as e:
        logger.error(f"获取系统信息失败: {e}")
        raise HTTPException(status_code=500, detail="获取系统信息失败")

@app.get("/health", response_model=HealthCheck)
async def health_check():
    """健康检查"""
    return HealthCheck(
        status="healthy",
        message="DT-Study-Companion运行正常"
    )

# ===== 根路径 =====

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "欢迎使用DT-Study-Companion API",
        "version": "1.0.0",
        "docs": "/docs"
    }

if __name__ == "__main__":
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
