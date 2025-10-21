#!/usr/bin/env python3
"""测试API服务器"""
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """测试导入"""
    print("🔍 测试模块导入...")
    
    try:
        import fastapi
        print("✓ FastAPI 导入成功")
    except ImportError as e:
        print(f"❌ FastAPI 导入失败: {e}")
        return False
    
    try:
        import uvicorn
        print("✓ Uvicorn 导入成功")
    except ImportError as e:
        print(f"❌ Uvicorn 导入失败: {e}")
        return False
    
    try:
        import requests
        print("✓ Requests 导入成功")
    except ImportError as e:
        print(f"❌ Requests 导入失败: {e}")
        return False
    
    return True

def test_api_import():
    """测试API模块导入"""
    print("🔍 测试API模块导入...")
    
    try:
        from api.rag_api import app
        print("✓ API模块导入成功")
        return True
    except Exception as e:
        print(f"❌ API模块导入失败: {e}")
        return False

def test_config():
    """测试配置"""
    print("🔍 测试配置...")
    
    try:
        from src.utils.config import Config
        print(f"✓ 配置加载成功")
        print(f"  - API端口: {Config.API_PORT}")
        print(f"  - API主机: {Config.API_HOST}")
        return True
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        return False

def main():
    """主函数"""
    print("=== API服务器测试 ===")
    
    # 测试导入
    if not test_imports():
        print("❌ 依赖包测试失败")
        return
    
    # 测试配置
    if not test_config():
        print("❌ 配置测试失败")
        return
    
    # 测试API模块
    if not test_api_import():
        print("❌ API模块测试失败")
        return
    
    print("✅ 所有测试通过！")
    print("🚀 可以启动API服务器了")

if __name__ == "__main__":
    main()
