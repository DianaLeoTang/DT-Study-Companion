#!/usr/bin/env python3
"""
清理旧文件脚本
将旧的文件移动到archive目录，保持项目整洁
"""
import os
import shutil
from pathlib import Path
from loguru import logger

def setup_logging():
    """设置日志"""
    logger.remove()
    logger.add(
        lambda msg: print(msg, end=""),
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level="INFO"
    )

def create_archive_structure():
    """创建归档目录结构"""
    archive_dir = Path("archive")
    archive_dir.mkdir(exist_ok=True)
    
    subdirs = [
        "old_scripts",
        "old_tests", 
        "old_docs",
        "old_frontend",
        "duplicate_files"
    ]
    
    for subdir in subdirs:
        (archive_dir / subdir).mkdir(exist_ok=True)
        logger.info(f"✓ 创建归档目录: {subdir}")

def move_old_files():
    """移动旧文件到归档目录"""
    logger.info("📦 开始整理旧文件...")
    
    # 旧脚本文件
    old_scripts = [
        "start_rag_system.py",
        "start_api_simple.py", 
        "fix_and_start.py",
        "quick_start.py",
        "simple_api_server.py",
        "test_api.py",
        "demo_rag.py",
        "test_rag_system.py",
        "test_docx_processing.py",
        "test_ocr.py",
        "test_ocr_simple.py",
        "test_pdf.py",
        "run_simple.py"
    ]
    
    for script in old_scripts:
        if Path(script).exists():
            shutil.move(script, f"archive/old_scripts/{script}")
            logger.info(f"✓ 移动脚本: {script}")
    
    # 旧文档文件
    old_docs = [
        "RAG_README.md",
        "RAG_SYSTEM_SUMMARY.md", 
        "PROJECT_SUMMARY.md",
        "build.md",
        "INSTALL.md"
    ]
    
    for doc in old_docs:
        if Path(doc).exists():
            shutil.move(doc, f"archive/old_docs/{doc}")
            logger.info(f"✓ 移动文档: {doc}")
    
    # 旧前端文件
    old_frontend_files = [
        "frontend/index.html",
        "frontend/rag_interface.html"
    ]
    
    for frontend_file in old_frontend_files:
        if Path(frontend_file).exists():
            shutil.move(frontend_file, f"archive/old_frontend/{Path(frontend_file).name}")
            logger.info(f"✓ 移动前端文件: {frontend_file}")

def create_new_structure_summary():
    """创建新结构说明"""
    summary = """
# 项目结构整理完成

## 🎯 新的项目结构

### 后端 (backend/)
- `app/` - 应用核心代码
  - `api/` - API路由 (auth, documents, queries, health)
  - `core/` - 核心配置 (config.py)
  - `models/` - 数据模型
  - `services/` - 业务服务
  - `main.py` - 应用入口
- `rag/` - RAG核心模块
  - `agents/` - RAG代理
  - `preprocessing/` - 文档预处理
  - `vectorstore/` - 向量存储
  - `llm/` - 大语言模型

### 前端 (frontend/)
- `public/` - 静态资源
  - `index.html` - 现代化主页面

### 数据 (data/)
- `documents/` - 原始文档
- `processed/` - 处理后的数据
- `database/` - 数据库文件

## 🚀 启动新系统

```bash
# 启动新的现代化系统
python start_new_system.py
```

## 📚 文档

- `README_NEW.md` - 新系统说明文档
- `PROJECT_STRUCTURE.md` - 项目结构设计文档

## 🗂️ 归档文件

旧文件已移动到 `archive/` 目录：
- `old_scripts/` - 旧脚本文件
- `old_docs/` - 旧文档文件  
- `old_frontend/` - 旧前端文件
- `duplicate_files/` - 重复文件

## ✨ 改进点

1. **前后端分离**: 清晰的架构设计
2. **模块化**: 可维护的代码结构
3. **现代化**: 最新的技术栈
4. **文档完善**: 详细的说明文档
5. **专业结构**: 符合行业标准
"""
    
    with open("STRUCTURE_CLEANUP.md", "w", encoding="utf-8") as f:
        f.write(summary)
    
    logger.info("✓ 创建结构整理说明文档")

def main():
    """主函数"""
    setup_logging()
    
    logger.info("=== 项目结构整理 ===")
    logger.info("🧹 开始清理旧文件...")
    
    # 创建归档目录
    create_archive_structure()
    
    # 移动旧文件
    move_old_files()
    
    # 创建说明文档
    create_new_structure_summary()
    
    logger.info("✅ 项目结构整理完成！")
    logger.info("📁 旧文件已移动到 archive/ 目录")
    logger.info("🚀 现在可以使用 python start_new_system.py 启动新系统")

if __name__ == "__main__":
    main()
