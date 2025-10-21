#!/usr/bin/env python3
"""
处理所有DOCX文件并创建向量库
每本书创建一个独立的collection
"""
import sys
import os
import re
from pathlib import Path
from loguru import logger

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.preprocessing.docx_parser import DOCXParser
from src.preprocessing.vectorstore_builder import VectorStoreBuilder

def setup_logging():
    """设置日志"""
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level="INFO"
    )

def clean_collection_name(filename: str) -> str:
    """清理文件名，生成合法的collection名称"""
    # 移除扩展名
    name = Path(filename).stem
    
    # 移除特殊字符，只保留字母、数字、下划线和中文
    name = re.sub(r'[^\w\u4e00-\u9fff]', '_', name)
    
    # 移除连续的下划线
    name = re.sub(r'_+', '_', name)
    
    # 移除开头和结尾的下划线
    name = name.strip('_')
    
    # 限制长度
    if len(name) > 50:
        name = name[:50]
    
    # 添加前缀
    collection_name = f"docx_{name}"
    
    return collection_name

def process_all_docx():
    """处理所有DOCX文件"""
    setup_logging()
    
    logger.info("=== 开始处理DOCX文件并创建向量库 ===")
    
    # 查找所有DOCX文件
    data_dir = Path("data")
    docx_files = list(data_dir.glob("*.docx"))
    
    if not docx_files:
        logger.error("❌ 未找到DOCX文件")
        return
    
    logger.info(f"📚 找到 {len(docx_files)} 个DOCX文件")
    for i, file in enumerate(docx_files, 1):
        logger.info(f"  {i}. {file.name} ({file.stat().st_size / 1024 / 1024:.1f}MB)")
    
    # 创建解析器和向量存储构建器
    parser = DOCXParser()
    builder = VectorStoreBuilder()
    
    # 处理每个文件
    all_chunks = {}
    
    for i, docx_file in enumerate(docx_files, 1):
        logger.info(f"\n📖 处理文件 {i}/{len(docx_files)}: {docx_file.name}")
        
        try:
            # 解析DOCX文件
            logger.info("  ⏳ 正在解析DOCX...")
            chunks = parser.parse_docx(str(docx_file))
            
            if not chunks:
                logger.warning(f"  ⚠️  {docx_file.name} 解析结果为空，跳过")
                continue
            
            logger.info(f"  ✓ 解析完成，共 {len(chunks)} 个文本块")
            
            # 添加元数据
            book_id = f"book_{i}"
            book_name = docx_file.stem
            
            for chunk in chunks:
                chunk["metadata"]["book_id"] = book_id
                chunk["metadata"]["book_name"] = book_name
                chunk["metadata"]["version"] = "1"
                chunk["metadata"]["filename"] = docx_file.name
                chunk["metadata"]["file_type"] = "docx"
            
            # 生成collection名称
            collection_name = clean_collection_name(docx_file.name)
            logger.info(f"  📦 Collection名称: {collection_name}")
            
            # 保存到字典
            all_chunks[collection_name] = chunks
            
            logger.info(f"  ✅ {docx_file.name} 处理完成")
            
        except Exception as e:
            logger.error(f"  ❌ 处理失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            continue
    
    if not all_chunks:
        logger.error("❌ 没有成功处理任何文档")
        return
    
    # 构建向量数据库
    logger.info(f"\n🔨 开始构建向量数据库...")
    logger.info(f"   总共 {len(all_chunks)} 个collections")
    logger.info(f"   总共 {sum(len(chunks) for chunks in all_chunks.values())} 个文本块")
    
    try:
        builder.build_all_collections(all_chunks, force_rebuild=True)
        logger.info("✅ 向量数据库构建完成")
        
        # 显示结果
        logger.info("\n📊 处理结果汇总:")
        for collection_name, chunks in all_chunks.items():
            logger.info(f"  ✓ {collection_name}: {len(chunks)} 个文本块")
        
        # 保存处理摘要
        import json
        summary = {
            "total_collections": len(all_chunks),
            "total_chunks": sum(len(chunks) for chunks in all_chunks.values()),
            "collections": {}
        }
        
        for collection_name, chunks in all_chunks.items():
            summary["collections"][collection_name] = {
                "chunk_count": len(chunks),
                "file_type": "docx",
                "source_file": chunks[0]["metadata"]["filename"] if chunks else "unknown"
            }
        
        output_dir = Path("data/processed")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        with open(output_dir / "docx_processing_summary.json", 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✓ 处理摘要已保存到: {output_dir / 'docx_processing_summary.json'}")
        
        logger.info("\n🎉 所有文档处理完成！")
        logger.info("💡 现在可以启动后端API进行问答了")
        
    except Exception as e:
        logger.error(f"❌ 向量数据库构建失败: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    process_all_docx()
