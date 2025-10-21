#!/usr/bin/env python3
"""
简单直接的向量库构建脚本
直接使用ChromaDB和sentence-transformers，不依赖langchain
"""
import sys
import re
from pathlib import Path
from loguru import logger
import chromadb
from sentence_transformers import SentenceTransformer

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.preprocessing.docx_parser import DOCXParser

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
    name = Path(filename).stem
    # 移除特殊字符
    name = re.sub(r'[^\w\u4e00-\u9fff]', '_', name)
    name = re.sub(r'_+', '_', name).strip('_')
    # 限制长度
    name = name[:50] if len(name) > 50 else name
    return f"docx_{name}"

def main():
    setup_logging()
    
    logger.info("=== 构建向量数据库 ===")
    
    # 1. 初始化ChromaDB
    logger.info("📦 初始化ChromaDB...")
    chroma_path = "./database/chroma_db"
    client = chromadb.PersistentClient(path=chroma_path)
    logger.info(f"✓ ChromaDB路径: {chroma_path}")
    
    # 2. 初始化Embedding模型
    logger.info("🤖 加载Embedding模型...")
    try:
        # 使用轻量级中文模型
        model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        logger.info("✓ Embedding模型加载成功")
    except Exception as e:
        logger.error(f"❌ Embedding模型加载失败: {e}")
        return
    
    # 3. 查找所有DOCX文件
    logger.info("📚 查找DOCX文件...")
    data_dir = Path("data")
    docx_files = list(data_dir.glob("*.docx"))
    
    if not docx_files:
        logger.error("❌ 未找到DOCX文件")
        return
    
    logger.info(f"找到 {len(docx_files)} 个DOCX文件:")
    for i, file in enumerate(docx_files, 1):
        logger.info(f"  {i}. {file.name}")
    
    # 4. 处理每个DOCX文件
    parser = DOCXParser()
    
    for i, docx_file in enumerate(docx_files, 1):
        logger.info(f"\n📖 [{i}/{len(docx_files)}] 处理: {docx_file.name}")
        
        try:
            # 生成collection名称
            collection_name = clean_collection_name(docx_file.name)
            logger.info(f"  Collection: {collection_name}")
            
            # 检查是否已存在
            try:
                existing = client.get_collection(collection_name)
                logger.info(f"  ⚠️  Collection已存在，删除重建...")
                client.delete_collection(collection_name)
            except:
                pass
            
            # 创建collection
            collection = client.create_collection(
                name=collection_name,
                metadata={"source": docx_file.name}
            )
            
            # 解析DOCX
            logger.info("  ⏳ 解析DOCX...")
            chunks = parser.parse_docx(str(docx_file))
            
            if not chunks:
                logger.warning("  ⚠️  解析结果为空，跳过")
                continue
            
            logger.info(f"  ✓ 解析完成: {len(chunks)} 个文本块")
            
            # 准备数据
            logger.info("  ⏳ 生成向量...")
            documents = []
            metadatas = []
            ids = []
            
            for j, chunk in enumerate(chunks):
                documents.append(chunk["content"])
                metadatas.append({
                    "book_name": docx_file.stem,
                    "filename": docx_file.name,
                    "chapter": chunk["metadata"].get("chapter", "未知章节"),
                    "chunk_id": j
                })
                ids.append(f"{collection_name}_{j}")
            
            # 批量处理，每次100个
            batch_size = 100
            for start_idx in range(0, len(documents), batch_size):
                end_idx = min(start_idx + batch_size, len(documents))
                batch_docs = documents[start_idx:end_idx]
                batch_metas = metadatas[start_idx:end_idx]
                batch_ids = ids[start_idx:end_idx]
                
                # 生成embeddings
                embeddings = model.encode(batch_docs).tolist()
                
                # 添加到collection
                collection.add(
                    embeddings=embeddings,
                    documents=batch_docs,
                    metadatas=batch_metas,
                    ids=batch_ids
                )
                
                logger.info(f"  ✓ 已处理 {end_idx}/{len(documents)} 个文本块")
            
            logger.info(f"  ✅ {docx_file.name} 处理完成")
            
        except Exception as e:
            logger.error(f"  ❌ 处理失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            continue
    
    # 5. 显示结果
    logger.info("\n📊 向量库构建完成！")
    logger.info("可用的Collections:")
    collections = client.list_collections()
    for coll in collections:
        count = coll.count()
        logger.info(f"  ✓ {coll.name}: {count} 个文档")
    
    logger.info("\n🎉 全部完成！现在可以启动后端进行问答了")

if __name__ == "__main__":
    main()
