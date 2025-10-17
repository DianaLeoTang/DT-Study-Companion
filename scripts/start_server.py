#!/usr/bin/env python3
"""
DT-Study-Companion 启动脚本
"""
import os
import sys
import subprocess
import argparse
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 8):
        print("❌ 错误: 需要Python 3.8或更高版本")
        print(f"当前版本: {sys.version}")
        sys.exit(1)
    print(f"✅ Python版本检查通过: {sys.version.split()[0]}")

def check_dependencies():
    """检查依赖是否安装"""
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        import langchain
        print("✅ 核心依赖检查通过")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请运行: pip install -r requirement.txt")
        return False

def check_env_file():
    """检查环境变量文件"""
    env_file = Path(".env")
    env_example = Path("env.example")
    
    if not env_file.exists():
        if env_example.exists():
            print("⚠️  未找到.env文件，正在从env.example创建...")
            subprocess.run(["cp", "env.example", ".env"])
            print("✅ 已创建.env文件，请编辑其中的配置")
            return False
        else:
            print("❌ 未找到环境变量配置文件")
            return False
    
    print("✅ 环境变量文件检查通过")
    return True

def check_data_directories():
    """检查数据目录"""
    dirs_to_create = [
        "data/raw_pdfs",
        "data/processed", 
        "database/chroma_db",
        "logs"
    ]
    
    for dir_path in dirs_to_create:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    print("✅ 数据目录检查完成")

def check_books_metadata():
    """检查书籍元数据文件"""
    metadata_file = Path("data/books_metadata.json")
    if not metadata_file.exists():
        print("❌ 未找到书籍元数据文件: data/books_metadata.json")
        return False
    
    print("✅ 书籍元数据文件检查通过")
    return True

def start_server(host="0.0.0.0", port=8000, reload=False):
    """启动服务器"""
    print(f"🚀 启动DT-Study-Companion服务器...")
    print(f"   地址: http://{host}:{port}")
    print(f"   API文档: http://{host}:{port}/docs")
    print(f"   前端界面: file://{os.path.abspath('frontend/index.html')}")
    print()
    
    try:
        cmd = [
            sys.executable, "-m", "uvicorn",
            "api.main:app",
            "--host", host,
            "--port", str(port)
        ]
        
        if reload:
            cmd.append("--reload")
        
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")

def main():
    parser = argparse.ArgumentParser(description="DT-Study-Companion 启动脚本")
    parser.add_argument("--host", default="0.0.0.0", help="服务器地址 (默认: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="服务器端口 (默认: 8000)")
    parser.add_argument("--reload", action="store_true", help="启用热重载 (开发模式)")
    parser.add_argument("--skip-checks", action="store_true", help="跳过环境检查")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🎓 DT-Study-Companion 启动检查")
    print("=" * 60)
    
    if not args.skip_checks:
        # 执行检查
        checks = [
            check_python_version,
            check_dependencies,
            check_env_file,
            check_data_directories,
            check_books_metadata
        ]
        
        all_passed = True
        for check in checks:
            if not check():
                all_passed = False
        
        if not all_passed:
            print("\n❌ 环境检查未通过，请解决上述问题后重试")
            print("💡 提示: 使用 --skip-checks 跳过检查直接启动")
            sys.exit(1)
        
        print("\n✅ 所有检查通过！")
    
    print("\n" + "=" * 60)
    start_server(args.host, args.port, args.reload)

if __name__ == "__main__":
    main()
