#!/usr/bin/env python3
"""快速启动RAG系统"""
import sys
import os
import subprocess
from pathlib import Path

def install_dependencies():
    """安装必要的依赖"""
    print("📦 检查并安装依赖...")
    
    required_packages = [
        "fastapi",
        "uvicorn[standard]", 
        "requests",
        "python-docx",
        "chromadb",
        "sentence-transformers",
        "langchain",
        "loguru"
    ]
    
    for package in required_packages:
        try:
            print(f"安装 {package}...")
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", package, "--break-system-packages"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✓ {package} 安装成功")
            else:
                print(f"⚠️ {package} 安装可能有问题: {result.stderr}")
        except Exception as e:
            print(f"❌ 安装 {package} 失败: {e}")

def start_api():
    """启动API服务器"""
    print("🚀 启动API服务器...")
    
    try:
        # 设置环境变量
        os.environ['API_PORT'] = '8000'
        os.environ['API_HOST'] = '0.0.0.0'
        
        # 直接运行API服务器
        result = subprocess.run([
            sys.executable, "api/rag_api.py"
        ], cwd=Path(__file__).parent)
        
    except KeyboardInterrupt:
        print("\n🛑 服务器已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")

def main():
    """主函数"""
    print("=== DT Study Companion 快速启动 ===")
    
    # 检查Python版本
    if sys.version_info < (3, 8):
        print("❌ 需要Python 3.8或更高版本")
        return
    
    print(f"✓ Python版本: {sys.version}")
    
    # 安装依赖
    install_dependencies()
    
    # 启动API服务器
    start_api()

if __name__ == "__main__":
    main()
