#!/usr/bin/env python3
"""简化的API服务器启动脚本"""
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def check_dependencies():
    """检查必要的依赖"""
    missing_deps = []
    
    try:
        import fastapi
        print("✓ FastAPI 已安装")
    except ImportError:
        missing_deps.append("fastapi")
    
    try:
        import uvicorn
        print("✓ Uvicorn 已安装")
    except ImportError:
        missing_deps.append("uvicorn")
    
    try:
        import requests
        print("✓ Requests 已安装")
    except ImportError:
        missing_deps.append("requests")
    
    if missing_deps:
        print(f"❌ 缺少依赖: {', '.join(missing_deps)}")
        print("请运行: pip install " + " ".join(missing_deps))
        return False
    
    return True

def start_server():
    """启动API服务器"""
    if not check_dependencies():
        return False
    
    print("🚀 启动RAG API服务器...")
    
    try:
        # 设置环境变量
        os.environ['API_PORT'] = '8000'
        os.environ['API_HOST'] = '0.0.0.0'
        
        # 导入并启动API
        from api.rag_api import app
        import uvicorn
        
        print("✅ API服务器配置完成")
        print("🌐 访问地址: http://localhost:8000")
        print("📖 API文档: http://localhost:8000/docs")
        print("💡 按 Ctrl+C 停止服务器")
        
        # 启动服务器
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="info",
            reload=False
        )
        
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        return False

if __name__ == "__main__":
    start_server()
