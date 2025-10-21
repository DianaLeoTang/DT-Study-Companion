"""批量处理PDF书籍并构建向量数据库"""
import sys
import os
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from loguru import logger
from src.preprocessing.pdf_parser import PDFParser
from src.preprocessing.vectorstore_builder import VectorStoreBuilder
from src.utils.config import Config
import json

def main(force_rebuild: bool = False,
         only_book_ids=None,
         only_versions=None,
         max_pages: int = None):
    """
    主处理流程
    
    Args:
        force_rebuild: 是否强制重建已存在的collection
    """
    logger.info("="*60)
    logger.info("开始批量处理PDF书籍")
    logger.info("="*60)
    
    # 1. 加载书籍元数据
    logger.info("\n步骤1: 加载书籍元数据")
    metadata = Config.load_books_metadata()
    total_books = len(metadata["books"])
    total_versions = sum(len(book["versions"]) for book in metadata["books"])
    logger.info(f"找到 {total_books} 本书，共 {total_versions} 个版本")
    
    # 2. 解析PDF
    logger.info("\n步骤2: 解析PDF文件")
    parser = PDFParser()
    
    try:
        all_chunks = parser.batch_parse(
            metadata,
            book_ids=only_book_ids,
            versions=only_versions,
            max_pages=max_pages
        )
        logger.info(f"✓ PDF解析完成，生成 {len(all_chunks)} 个collections")
        
        # 统计信息
        total_chunks = sum(len(chunks) for chunks in all_chunks.values())
        logger.info(f"  总文本块数: {total_chunks}")
        
        # 保存解析结果（可选）
        processed_dir = Config.PROCESSED_DIR
        os.makedirs(processed_dir, exist_ok=True)
        
        chunks_summary = {
            collection: len(chunks)
            for collection, chunks in all_chunks.items()
        }
        
        summary_file = os.path.join(processed_dir, "chunks_summary.json")
        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump(chunks_summary, f, ensure_ascii=False, indent=2)
        
        logger.info(f"  摘要已保存: {summary_file}")
        
    except Exception as e:
        logger.error(f"✗ PDF解析失败: {e}")
        return False
    
    # 3. 构建向量数据库
    logger.info("\n步骤3: 构建向量数据库")
    builder = VectorStoreBuilder()
    
    try:
        builder.build_all_collections(all_chunks, force_rebuild=force_rebuild)
        logger.info("✓ 向量数据库构建完成")
        
        # 验证collections
        collections = builder.list_collections()
        logger.info(f"  可用collections: {len(collections)}")
        for collection in collections:
            doc_count = builder.get_vectorstore(collection)._collection.count() if builder.get_vectorstore(collection) else 0
            logger.info(f"    - {collection}: {doc_count} 个文档")
        
    except Exception as e:
        logger.error(f"✗ 向量数据库构建失败: {e}")
        return False
    
    logger.info("\n"+"="*60)
    logger.info("✅ 所有处理完成！")
    logger.info("="*60)
    
    return True

def check_pdf_files():
    """检查PDF文件是否存在"""
    logger.info("检查PDF文件...")
    
    metadata = Config.load_books_metadata()
    missing_files = []
    
    for book in metadata["books"]:
        for version_info in book["versions"]:
            filename = version_info["filename"]
            pdf_path = os.path.join(Config.RAW_PDFS_DIR, filename)
            
            if not os.path.exists(pdf_path):
                missing_files.append(filename)
                logger.warning(f"  ✗ 缺失: {filename}")
            else:
                logger.info(f"  ✓ 存在: {filename}")
    
    if missing_files:
        logger.warning(f"\n缺失 {len(missing_files)} 个PDF文件")
        logger.warning("请将缺失的PDF文件放入 data/raw_pdfs/ 目录")
        return False
    
    logger.info(f"✓ 所有PDF文件已准备就绪")
    return True

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="批量处理PDF书籍")
    parser.add_argument(
        "--force", 
        action="store_true",
        help="强制重建已存在的collection"
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="仅检查PDF文件是否存在"
    )
    parser.add_argument(
        "--book",
        type=str,
        help="仅处理指定书籍ID，多个用逗号分隔，例如: epidemiology"
    )
    parser.add_argument(
        "--version",
        type=str,
        help="仅处理指定版本，多个用逗号分隔，例如: 8,9 或 wangyan_v2"
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        help="每本书最多解析的页数（用于快速验证）"
    )
    
    args = parser.parse_args()
    
    if args.check_only:
        # 仅检查文件
        check_pdf_files()
    else:
        # 先检查文件
        if not check_pdf_files():
            logger.error("请先准备好所有PDF文件")
            sys.exit(1)
        
        # 执行处理
        only_book_ids = args.book.split(',') if args.book else None
        only_versions = args.version.split(',') if args.version else None
        success = main(
            force_rebuild=args.force,
            only_book_ids=only_book_ids,
            only_versions=only_versions,
            max_pages=args.max_pages
        )
        sys.exit(0 if success else 1)