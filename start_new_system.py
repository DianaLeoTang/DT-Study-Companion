#!/usr/bin/env python3
"""
DT Study Companion - 新系统启动脚本
现代化的前后端分离架构
"""
import sys
import os
import subprocess
import time
import webbrowser
from pathlib import Path
from loguru import logger

def setup_logging():
    """设置日志"""
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level="INFO"
    )

def check_dependencies():
    """检查依赖"""
    logger.info("🔍 检查系统依赖...")
    
    required_packages = [
        "fastapi",
        "uvicorn", 
        "python-docx",
        "chromadb",
        "sentence-transformers",
        "langchain",
        "loguru"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            logger.info(f"✓ {package}")
        except ImportError:
            missing_packages.append(package)
            logger.warning(f"❌ {package}")
    
    if missing_packages:
        logger.warning(f"缺少依赖包: {', '.join(missing_packages)}")
        logger.info("尝试自动安装依赖...")
        
        for package in missing_packages:
            if package == "docx":
                package_name = "python-docx"
            else:
                package_name = package
            
            logger.info(f"正在安装 {package_name}...")
            try:
                result = subprocess.run([
                    sys.executable, "-m", "pip", "install", package_name, "--break-system-packages"
                ], capture_output=True, text=True, timeout=60)
                
                if result.returncode == 0:
                    logger.info(f"✓ {package_name} 安装成功")
                else:
                    logger.error(f"✗ {package_name} 安装失败: {result.stderr}")
            except Exception as e:
                logger.error(f"安装 {package_name} 时出错: {e}")
    
    logger.info("✅ 依赖检查完成")
    return True

def create_directories():
    """创建必要的目录"""
    logger.info("📁 创建项目目录...")
    
    directories = [
        "data/documents/pdfs",
        "data/documents/docx", 
        "data/documents/metadata",
        "data/processed/chunks",
        "data/processed/vectors",
        "data/database",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"✓ {directory}")
    
    logger.info("✅ 目录创建完成")

def start_backend():
    """启动后端服务"""
    logger.info("🚀 启动后端服务...")
    
    try:
        # 设置环境变量
        os.environ['API_HOST'] = '0.0.0.0'
        os.environ['API_PORT'] = '8000'
        
        # 启动后端服务
        backend_process = subprocess.Popen([
            sys.executable, "backend/app/main.py"
        ], cwd=Path(__file__).parent)
        
        # 等待服务启动
        time.sleep(3)
        
        # 检查服务是否运行
        import requests
        try:
            response = requests.get("http://localhost:8000/api/health", timeout=5)
            if response.status_code == 200:
                logger.info("✅ 后端服务启动成功")
                return backend_process
            else:
                logger.error("❌ 后端服务响应异常")
                return None
        except requests.exceptions.RequestException:
            logger.error("❌ 无法连接到后端服务")
            return None
            
    except Exception as e:
        logger.error(f"❌ 启动后端服务失败: {e}")
        return None

def open_frontend():
    """打开前端界面"""
    logger.info("🌐 打开前端界面...")
    
    try:
        webbrowser.open("http://localhost:8000")
        logger.info("✅ 前端界面已打开")
    except Exception as e:
        logger.error(f"❌ 打开前端界面失败: {e}")

def main():
    """主函数"""
    setup_logging()
    
    logger.info("=== DT Study Companion 新系统启动 ===")
    logger.info("🏗️ 现代化前后端分离架构")
    
    # 1. 检查依赖
    if not check_dependencies():
        logger.error("❌ 依赖检查失败")
        return 1
    
    # 2. 创建目录
    create_directories()
    
    # 3. 启动后端服务
    backend_process = start_backend()
    if not backend_process:
        logger.error("❌ 后端服务启动失败")
        return 1
    
    # 4. 打开前端界面
    open_frontend()
    
    logger.info("=== 系统启动完成 ===")
    logger.info("🌐 前端地址: http://localhost:8000")
    logger.info("📖 API文档: http://localhost:8000/api/docs")
    logger.info("💡 按 Ctrl+C 停止服务")
    
    try:
        # 保持服务运行
        backend_process.wait()
    except KeyboardInterrupt:
        logger.info("🛑 正在停止服务...")
        backend_process.terminate()
        backend_process.wait()
        logger.info("✅ 服务已停止")
    
    return 0

if __name__ == "__main__":
    exit(main())
