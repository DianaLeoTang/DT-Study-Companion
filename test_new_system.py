#!/usr/bin/env python3
"""
测试新系统 - 简化版本
"""
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """测试模块导入"""
    print("🔍 测试模块导入...")
    
    try:
        from backend.app.core.config import Config
        print("✓ 配置模块导入成功")
    except Exception as e:
        print(f"❌ 配置模块导入失败: {e}")
        return False
    
    try:
        from backend.app.api import health, queries, documents, auth
        print("✓ API模块导入成功")
    except Exception as e:
        print(f"❌ API模块导入失败: {e}")
        return False
    
    return True

def test_config():
    """测试配置"""
    print("🔍 测试配置...")
    
    try:
        from backend.app.core.config import Config
        
        # 设置环境变量
        os.environ['API_HOST'] = '0.0.0.0'
        os.environ['API_PORT'] = '8000'
        
        print(f"✓ API主机: {Config.API_HOST}")
        print(f"✓ API端口: {Config.API_PORT}")
        print(f"✓ 数据目录: {Config.DATA_DIR}")
        
        return True
    except Exception as e:
        print(f"❌ 配置测试失败: {e}")
        return False

def test_api_creation():
    """测试API创建"""
    print("🔍 测试API创建...")
    
    try:
        from backend.app.main import app
        print("✓ FastAPI应用创建成功")
        
        # 检查路由
        routes = [route.path for route in app.routes]
        print(f"✓ 可用路由: {len(routes)} 个")
        
        return True
    except Exception as e:
        print(f"❌ API创建失败: {e}")
        return False

def main():
    """主函数"""
    print("=== 新系统测试 ===")
    print("🧪 测试现代化RAG系统...")
    
    # 测试导入
    if not test_imports():
        print("❌ 模块导入测试失败")
        return 1
    
    # 测试配置
    if not test_config():
        print("❌ 配置测试失败")
        return 1
    
    # 测试API创建
    if not test_api_creation():
        print("❌ API创建测试失败")
        return 1
    
    print("✅ 所有测试通过！")
    print("🚀 新系统准备就绪")
    print("💡 运行 'python start_new_system.py' 启动完整系统")
    
    return 0

if __name__ == "__main__":
    exit(main())
