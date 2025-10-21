#!/usr/bin/env python3
"""文档处理脚本 - 支持PDF和DOCX文件"""
import os
import sys
import json
import argparse
from pathlib import Path
from loguru import logger

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.preprocessing.pdf_parser import PDFParser
from src.preprocessing.docx_parser import DOCXParser
from src.preprocessing.vectorstore_builder import VectorStoreBuilder
from src.utils.config import Config

def setup_logging():
    """设置日志"""
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO"
    )

def process_single_file(file_path: str, file_type: str = None) -> dict:
    """处理单个文件"""
    file_path = Path(file_path)
    
    if not file_path.exists():
        logger.error(f"文件不存在: {file_path}")
        return {}
    
    # 自动检测文件类型
    if file_type is None:
        if file_path.suffix.lower() == '.pdf':
            file_type = 'pdf'
        elif file_path.suffix.lower() == '.docx':
            file_type = 'docx'
        else:
            logger.error(f"不支持的文件类型: {file_path.suffix}")
            return {}
    
    logger.info(f"开始处理 {file_type.upper()} 文件: {file_path.name}")
    
    try:
        if file_type == 'pdf':
            parser = PDFParser()
            chunks = parser.parse_pdf(str(file_path))
        elif file_type == 'docx':
            parser = DOCXParser()
            chunks = parser.parse_docx(str(file_path))
        else:
            logger.error(f"不支持的文件类型: {file_type}")
            return {}
        
        # 添加文件信息到元数据
        for chunk in chunks:
            chunk["metadata"]["source_file"] = file_path.name
            chunk["metadata"]["file_type"] = file_type
        
        logger.info(f"✓ 文件解析完成: {len(chunks)} 个文本块")
        return {
            "file_name": file_path.name,
            "file_type": file_type,
            "chunks": chunks
        }
        
    except Exception as e:
        logger.error(f"✗ 文件处理失败: {e}")
        return {}

def process_directory(directory: str, file_types: list = None) -> dict:
    """处理目录中的所有文件"""
    if file_types is None:
        file_types = ['pdf', 'docx']
    
    directory = Path(directory)
    if not directory.exists():
        logger.error(f"目录不存在: {directory}")
        return {}
    
    all_results = {}
    
    # 查找所有支持的文件
    for file_type in file_types:
        pattern = f"*.{file_type}"
        files = list(directory.glob(pattern))
        
        logger.info(f"找到 {len(files)} 个 {file_type.upper()} 文件")
        
        for file_path in files:
            result = process_single_file(str(file_path), file_type)
            if result:
                collection_name = f"{file_path.stem}_{file_type}"
                all_results[collection_name] = result["chunks"]
    
    return all_results

def build_vectorstore(all_chunks: dict, force_rebuild: bool = False):
    """构建向量数据库"""
    if not all_chunks:
        logger.warning("没有可用的文本块，跳过向量数据库构建")
        return
    
    logger.info(f"开始构建向量数据库，共 {len(all_chunks)} 个collections")
    
    try:
        builder = VectorStoreBuilder()
        builder.build_all_collections(all_chunks, force_rebuild=force_rebuild)
        logger.info("✓ 向量数据库构建完成")
    except Exception as e:
        logger.error(f"✗ 向量数据库构建失败: {e}")
        raise

def save_processing_summary(all_chunks: dict, output_file: str):
    """保存处理摘要"""
    summary = {
        "total_collections": len(all_chunks),
        "total_chunks": sum(len(chunks) for chunks in all_chunks.values()),
        "collections": {}
    }
    
    for collection_name, chunks in all_chunks.items():
        summary["collections"][collection_name] = {
            "chunk_count": len(chunks),
            "file_type": chunks[0]["metadata"].get("file_type", "unknown") if chunks else "unknown",
            "source_file": chunks[0]["metadata"].get("source_file", "unknown") if chunks else "unknown"
        }
    
    # 确保输出目录存在
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    logger.info(f"处理摘要已保存到: {output_file}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="文档处理脚本")
    parser.add_argument("--input", "-i", required=True, help="输入文件或目录路径")
    parser.add_argument("--type", "-t", choices=['pdf', 'docx', 'both'], default='both', 
                       help="文件类型 (pdf/docx/both)")
    parser.add_argument("--output", "-o", help="输出摘要文件路径")
    parser.add_argument("--force-rebuild", "-f", action="store_true", 
                       help="强制重建向量数据库")
    parser.add_argument("--no-vectorstore", action="store_true", 
                       help="不构建向量数据库")
    
    args = parser.parse_args()
    
    # 设置日志
    setup_logging()
    
    # 验证配置
    if not Config.validate_config():
        logger.error("配置验证失败，请检查配置文件")
        return 1
    
    input_path = Path(args.input)
    all_chunks = {}
    
    if input_path.is_file():
        # 处理单个文件
        file_types = [args.type] if args.type != 'both' else ['pdf', 'docx']
        file_type = None
        for ft in file_types:
            if input_path.suffix.lower() == f'.{ft}':
                file_type = ft
                break
        
        if file_type is None:
            logger.error(f"文件类型不匹配: {input_path.suffix}")
            return 1
        
        result = process_single_file(str(input_path), file_type)
        if result:
            collection_name = f"{input_path.stem}_{file_type}"
            all_chunks[collection_name] = result["chunks"]
    
    elif input_path.is_dir():
        # 处理目录
        file_types = ['pdf', 'docx'] if args.type == 'both' else [args.type]
        all_chunks = process_directory(str(input_path), file_types)
    
    else:
        logger.error(f"输入路径不存在: {input_path}")
        return 1
    
    if not all_chunks:
        logger.warning("没有处理任何文件")
        return 0
    
    # 构建向量数据库
    if not args.no_vectorstore:
        build_vectorstore(all_chunks, args.force_rebuild)
    
    # 保存处理摘要
    if args.output:
        save_processing_summary(all_chunks, args.output)
    else:
        # 默认保存到processed目录
        default_output = Config.PROCESSED_DIR / "processing_summary.json"
        save_processing_summary(all_chunks, str(default_output))
    
    logger.info("文档处理完成！")
    return 0

if __name__ == "__main__":
    exit(main())
