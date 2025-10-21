#!/usr/bin/env python3
"""测试RAG系统"""
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.preprocessing.docx_parser import DOCXParser
from src.preprocessing.vectorstore_builder import VectorStoreBuilder
from src.agents.rag_agent import RAGAgent
from src.utils.config import Config

def test_docx_to_rag():
    """测试从DOCX文件到RAG的完整流程"""
    print("=== DOCX文件RAG系统测试 ===\n")
    
    # 1. 查找DOCX文件
    data_dir = Path("data")
    docx_files = list(data_dir.glob("*.docx"))
    
    if not docx_files:
        print("未找到DOCX文件")
        return False
    
    print(f"找到 {len(docx_files)} 个DOCX文件:")
    for file in docx_files:
        print(f"  - {file.name}")
    
    # 2. 解析第一个DOCX文件
    test_file = docx_files[0]
    print(f"\n解析文件: {test_file.name}")
    
    try:
        parser = DOCXParser()
        chunks = parser.parse_docx(str(test_file))
        print(f"✓ 解析完成，共 {len(chunks)} 个文本块")
        
        # 添加必要的元数据
        for chunk in chunks:
            chunk["metadata"]["book_id"] = "test_book"
            chunk["metadata"]["book_name"] = test_file.stem
            chunk["metadata"]["version"] = "1"
            chunk["metadata"]["filename"] = test_file.name
            chunk["metadata"]["file_type"] = "docx"
        
    except Exception as e:
        print(f"✗ 解析失败: {e}")
        return False
    
    # 3. 构建向量数据库
    print(f"\n构建向量数据库...")
    try:
        builder = VectorStoreBuilder()
        collection_name = f"test_{test_file.stem}_docx"
        vectorstore = builder.build_collection(
            collection_name=collection_name,
            chunks=chunks,
            force_rebuild=True
        )
        print(f"✓ 向量数据库构建完成: {collection_name}")
        
    except Exception as e:
        print(f"✗ 向量数据库构建失败: {e}")
        return False
    
    # 4. 创建RAG代理并测试
    print(f"\n创建RAG代理...")
    try:
        rag_agent = RAGAgent(vectorstore, collection_name)
        
        # 显示collection信息
        info = rag_agent.get_collection_info()
        print(f"Collection信息: {info}")
        
        # 测试问答
        test_questions = [
            "这本书的主要内容是什么？",
            "第一章讲了什么？",
            "请总结一下关键概念",
            "有什么重要的数据或统计信息？"
        ]
        
        print(f"\n开始测试问答...")
        for i, question in enumerate(test_questions, 1):
            print(f"\n--- 问题 {i} ---")
            print(f"问题: {question}")
            
            try:
                result = rag_agent.ask(question)
                print(f"答案: {result['answer'][:200]}...")
                print(f"使用了 {result['context_count']} 个相关文档")
                
                # 显示相关文档信息
                if result['context_documents']:
                    print("相关文档:")
                    for j, doc in enumerate(result['context_documents'][:2], 1):
                        print(f"  文档{j}: {doc['metadata'].get('chapter', '未知章节')} - {doc['content'][:50]}...")
                
            except Exception as e:
                print(f"✗ 问答失败: {e}")
        
        print(f"\n✓ RAG系统测试完成！")
        return True
        
    except Exception as e:
        print(f"✗ RAG代理创建失败: {e}")
        return False

def test_multiple_files():
    """测试多个文件的处理"""
    print("\n=== 多文件处理测试 ===\n")
    
    data_dir = Path("data")
    docx_files = list(data_dir.glob("*.docx"))
    
    if len(docx_files) < 2:
        print("文件数量不足，跳过多文件测试")
        return True
    
    # 处理前两个文件
    all_chunks = {}
    
    for i, file in enumerate(docx_files[:2]):
        print(f"处理文件 {i+1}: {file.name}")
        
        try:
            parser = DOCXParser()
            chunks = parser.parse_docx(str(file))
            
            # 添加元数据
            for chunk in chunks:
                chunk["metadata"]["book_id"] = f"book_{i+1}"
                chunk["metadata"]["book_name"] = file.stem
                chunk["metadata"]["version"] = "1"
                chunk["metadata"]["filename"] = file.name
                chunk["metadata"]["file_type"] = "docx"
            
            collection_name = f"multi_test_{file.stem}"
            all_chunks[collection_name] = chunks
            
            print(f"✓ 处理完成: {len(chunks)} 个文本块")
            
        except Exception as e:
            print(f"✗ 处理失败: {e}")
            continue
    
    if not all_chunks:
        print("没有成功处理任何文件")
        return False
    
    # 构建所有向量数据库
    print(f"\n构建 {len(all_chunks)} 个向量数据库...")
    try:
        builder = VectorStoreBuilder()
        builder.build_all_collections(all_chunks, force_rebuild=True)
        print("✓ 所有向量数据库构建完成")
        
        # 测试每个collection
        for collection_name in all_chunks.keys():
            print(f"\n测试collection: {collection_name}")
            vectorstore = builder.get_vectorstore(collection_name)
            if vectorstore:
                rag_agent = RAGAgent(vectorstore, collection_name)
                result = rag_agent.ask("这本书的主要内容是什么？")
                print(f"答案预览: {result['answer'][:100]}...")
            else:
                print("✗ 无法加载向量数据库")
        
        return True
        
    except Exception as e:
        print(f"✗ 多文件处理失败: {e}")
        return False

def main():
    """主函数"""
    print("开始RAG系统测试...\n")
    
    # 测试单个文件
    success1 = test_docx_to_rag()
    
    # 测试多个文件
    success2 = test_multiple_files()
    
    if success1 and success2:
        print("\n🎉 所有测试通过！RAG系统运行正常。")
    else:
        print("\n❌ 部分测试失败，请检查错误信息。")

if __name__ == "__main__":
    main()
