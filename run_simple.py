#!/usr/bin/env python3
"""
DT-Study-Companion 简化启动脚本
"""
import os
import sys
import uvicorn
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    print("🎓 DT-Study-Companion 简化启动")
    print("=" * 50)
    print("🚀 启动服务器...")
    print("   地址: http://localhost:8000")
    print("   API文档: http://localhost:8000/docs")
    print("   前端界面: file://" + str(project_root / "frontend" / "index.html"))
    print()
    print("按 Ctrl+C 停止服务器")
    print("=" * 50)
    
    try:
        uvicorn.run(
            "api.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        print("\n💡 可能的解决方案:")
        print("1. 检查是否安装了所有依赖: pip install -r requirement.txt")
        print("2. 检查端口8000是否被占用")
        print("3. 检查.env文件配置")

if __name__ == "__main__":
    main()
