#!/usr/bin/env python3
"""一键修复并启动RAG系统"""
import sys
import os
import subprocess
import time
from pathlib import Path

def run_command(cmd, description):
    """运行命令并显示结果"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ {description} 成功")
            return True
        else:
            print(f"❌ {description} 失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} 异常: {e}")
        return False

def main():
    """主函数"""
    print("=== 一键修复并启动RAG系统 ===")
    
    # 1. 安装必要的依赖
    print("\n📦 步骤1: 安装依赖包")
    dependencies = [
        "fastapi",
        "uvicorn[standard]",
        "requests", 
        "python-docx",
        "chromadb",
        "sentence-transformers",
        "langchain",
        "loguru",
        "pydantic"
    ]
    
    for dep in dependencies:
        cmd = f"{sys.executable} -m pip install {dep} --break-system-packages"
        run_command(cmd, f"安装 {dep}")
    
    # 2. 测试导入
    print("\n🔍 步骤2: 测试模块导入")
    try:
        import fastapi
        import uvicorn
        import requests
        print("✓ 核心依赖导入成功")
    except ImportError as e:
        print(f"❌ 依赖导入失败: {e}")
        print("请手动运行: pip install fastapi uvicorn requests --break-system-packages")
        return
    
    # 3. 启动API服务器
    print("\n🚀 步骤3: 启动API服务器")
    
    # 设置环境变量
    os.environ['API_PORT'] = '8000'
    os.environ['API_HOST'] = '0.0.0.0'
    
    print("🌐 API服务器地址: http://localhost:8000")
    print("📖 API文档地址: http://localhost:8000/docs")
    print("💡 按 Ctrl+C 停止服务器")
    
    try:
        # 直接启动API服务器
        from api.rag_api import app
        import uvicorn
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="info"
        )
        
    except KeyboardInterrupt:
        print("\n🛑 服务器已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        print("请检查错误信息并手动修复")

if __name__ == "__main__":
    main()
