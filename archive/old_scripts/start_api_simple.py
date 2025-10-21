#!/usr/bin/env python3
"""最简单的API服务器启动方式"""
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """直接启动API服务器"""
    print("🚀 启动RAG API服务器...")
    
    # 设置环境变量
    os.environ['API_PORT'] = '8000'
    os.environ['API_HOST'] = '0.0.0.0'
    
    try:
        # 直接导入并运行
        from api.rag_api import app
        import uvicorn
        
        print("✅ 模块加载成功")
        print("🌐 服务器地址: http://localhost:8000")
        print("📖 API文档: http://localhost:8000/docs")
        print("💡 按 Ctrl+C 停止服务器")
        
        # 启动服务器
        uvicorn.run(
            app,
            host="0.0.0.0", 
            port=8000,
            log_level="info"
        )
        
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        print("请先安装依赖: pip install fastapi uvicorn requests --break-system-packages")
    except Exception as e:
        print(f"❌ 启动失败: {e}")

if __name__ == "__main__":
    main()
