#!/usr/bin/env python3
"""测试DOCX处理功能"""
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.preprocessing.docx_parser import DOCXParser
from src.preprocessing.vectorstore_builder import VectorStoreBuilder
from src.utils.config import Config

def test_docx_parsing():
    """测试DOCX解析"""
    print("开始测试DOCX解析...")
    
    # 查找data目录中的docx文件
    data_dir = Path("data")
    docx_files = list(data_dir.glob("*.docx"))
    
    if not docx_files:
        print("未找到DOCX文件")
        return
    
    print(f"找到 {len(docx_files)} 个DOCX文件:")
    for file in docx_files:
        print(f"  - {file.name}")
    
    # 测试解析第一个docx文件
    test_file = docx_files[0]
    print(f"\n测试解析文件: {test_file.name}")
    
    try:
        parser = DOCXParser()
        chunks = parser.parse_docx(str(test_file))
        
        print(f"解析完成，共 {len(chunks)} 个文本块")
        
        # 显示前3个块的信息
        for i, chunk in enumerate(chunks[:3]):
            print(f"\n块 {i+1}:")
            print(f"  段落: {chunk['metadata']['paragraph']}")
            print(f"  章节: {chunk['metadata']['chapter']}")
            print(f"  内容长度: {len(chunk['content'])}")
            print(f"  内容预览: {chunk['content'][:100]}...")
        
        return chunks
        
    except Exception as e:
        print(f"解析失败: {e}")
        return None

def test_vectorstore_building(chunks):
    """测试向量库构建"""
    if not chunks:
        print("没有可用的文本块，跳过向量库测试")
        return
    
    print("\n开始测试向量库构建...")
    
    try:
        builder = VectorStoreBuilder()
        
        # 为测试添加元数据
        for chunk in chunks:
            chunk["metadata"]["book_id"] = "test_book"
            chunk["metadata"]["book_name"] = "测试书籍"
            chunk["metadata"]["version"] = "1"
            chunk["metadata"]["filename"] = "test.docx"
            chunk["metadata"]["file_type"] = "docx"
        
        # 构建测试collection
        collection_name = "test_docx_collection"
        vectorstore = builder.build_collection(
            collection_name=collection_name,
            chunks=chunks,
            force_rebuild=True
        )
        
        print(f"✓ 向量库构建成功: {collection_name}")
        
        # 测试检索
        print("\n测试检索功能...")
        test_query = "什么是"
        results = vectorstore.similarity_search(test_query, k=3)
        
        print(f"查询: '{test_query}'")
        print(f"找到 {len(results)} 个相关文档:")
        
        for i, doc in enumerate(results):
            print(f"\n结果 {i+1}:")
            print(f"  内容: {doc.page_content[:100]}...")
            print(f"  元数据: {doc.metadata}")
        
        return vectorstore
        
    except Exception as e:
        print(f"向量库构建失败: {e}")
        return None

def main():
    """主函数"""
    print("=== DOCX处理和RAG测试 ===\n")
    
    # 测试DOCX解析
    chunks = test_docx_parsing()
    
    if chunks:
        # 测试向量库构建
        vectorstore = test_vectorstore_building(chunks)
        
        if vectorstore:
            print("\n✓ 所有测试通过！")
        else:
            print("\n✗ 向量库测试失败")
    else:
        print("\n✗ DOCX解析测试失败")

if __name__ == "__main__":
    main()
