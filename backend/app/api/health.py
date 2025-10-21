"""
健康检查API路由
"""
from fastapi import APIRouter, Depends
from typing import Dict, Any
from loguru import logger

router = APIRouter()

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """健康检查接口"""
    return {
        "status": "healthy",
        "service": "DT Study Companion API",
        "version": "2.0.0"
    }

@router.get("/status")
async def system_status() -> Dict[str, Any]:
    """系统状态检查"""
    try:
        # 这里可以添加更详细的状态检查
        # 比如数据库连接、向量数据库状态等
        return {
            "status": "operational",
            "components": {
                "api": "healthy",
                "database": "healthy",
                "vectorstore": "healthy"
            }
        }
    except Exception as e:
        logger.error(f"系统状态检查失败: {e}")
        return {
            "status": "degraded",
            "error": str(e)
        }
