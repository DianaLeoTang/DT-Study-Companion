#!/usr/bin/env python3
"""
DT Study Companion - 后端主应用
现代化的RAG问答系统后端服务
"""
import sys
import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
from loguru import logger

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 导入配置
from backend.app.core.config import Config

# 导入API路由
from backend.app.api import health, queries, documents, auth

# 创建FastAPI应用
app = FastAPI(
    title="DT Study Companion API",
    description="基于RAG的智能问答系统后端API",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册API路由
app.include_router(health.router, prefix="/api", tags=["健康检查"])
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(documents.router, prefix="/api/documents", tags=["文档管理"])
app.include_router(queries.router, prefix="/api/queries", tags=["查询问答"])

# 静态文件服务
app.mount("/static", StaticFiles(directory="frontend/public"), name="static")

@app.get("/", response_class=HTMLResponse)
async def root():
    """根路径 - 返回前端页面"""
    try:
        with open("frontend/public/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="""
        <html>
            <head><title>DT Study Companion</title></head>
            <body>
                <h1>DT Study Companion API</h1>
                <p>后端服务正在运行</p>
                <p><a href="/api/docs">查看API文档</a></p>
            </body>
        </html>
        """)

@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info("🚀 DT Study Companion 后端服务启动中...")
    
    # 验证配置
    if not Config.validate_config():
        logger.error("❌ 配置验证失败")
        raise Exception("配置验证失败")
    
    logger.info("✅ 后端服务启动完成")
    logger.info(f"🌐 API文档: http://localhost:{Config.API_PORT}/api/docs")

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    logger.info("🛑 DT Study Companion 后端服务正在关闭...")

if __name__ == "__main__":
    import os
    
    # 从环境变量获取配置
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    
    logger.info("🚀 启动DT Study Companion后端服务...")
    logger.info(f"🌐 服务地址: http://{host}:{port}")
    logger.info(f"📖 API文档: http://{host}:{port}/api/docs")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=False,
        log_level="info"
    )
