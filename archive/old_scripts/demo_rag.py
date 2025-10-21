#!/usr/bin/env python3
"""RAG系统演示脚本"""
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

def demo_docx_processing():
    """演示DOCX处理功能"""
    print("=== DOCX文档处理演示 ===\n")
    
    # 查找DOCX文件
    data_dir = Path("data")
    docx_files = list(data_dir.glob("*.docx"))
    
    if not docx_files:
        print("❌ 未找到DOCX文件，请将DOCX文件放入data目录")
        return None
    
    print(f"📁 找到 {len(docx_files)} 个DOCX文件:")
    for i, file in enumerate(docx_files, 1):
        print(f"   {i}. {file.name}")
    
    # 选择第一个文件进行演示
    selected_file = docx_files[0]
    print(f"\n📖 演示文件: {selected_file.name}")
    
    try:
        # 解析DOCX文件
        print("🔄 正在解析DOCX文件...")
        parser = DOCXParser()
        chunks = parser.parse_docx(str(selected_file))
        
        print(f"✅ 解析完成！共生成 {len(chunks)} 个文本块")
        
        # 显示前几个块的信息
        print("\n📋 文本块示例:")
        for i, chunk in enumerate(chunks[:3], 1):
            print(f"\n   块 {i}:")
            print(f"   📄 段落: {chunk['metadata']['paragraph']}")
            print(f"   📚 章节: {chunk['metadata']['chapter']}")
            print(f"   📝 内容长度: {len(chunk['content'])} 字符")
            print(f"   💬 内容预览: {chunk['content'][:100]}...")
        
        # 添加元数据
        for chunk in chunks:
            chunk["metadata"]["book_id"] = "demo_book"
            chunk["metadata"]["book_name"] = selected_file.stem
            chunk["metadata"]["version"] = "1"
            chunk["metadata"]["filename"] = selected_file.name
            chunk["metadata"]["file_type"] = "docx"
        
        return chunks
        
    except Exception as e:
        print(f"❌ 解析失败: {e}")
        return None

def demo_vectorstore_building(chunks):
    """演示向量数据库构建"""
    if not chunks:
        print("❌ 没有可用的文本块，跳过向量数据库演示")
        return None
    
    print("\n=== 向量数据库构建演示 ===\n")
    
    try:
        print("🔄 正在构建向量数据库...")
        builder = VectorStoreBuilder()
        collection_name = "demo_collection"
        
        vectorstore = builder.build_collection(
            collection_name=collection_name,
            chunks=chunks,
            force_rebuild=True
        )
        
        print(f"✅ 向量数据库构建完成！")
        print(f"📊 Collection名称: {collection_name}")
        print(f"📈 文档数量: {len(chunks)}")
        
        return vectorstore, collection_name
        
    except Exception as e:
        print(f"❌ 向量数据库构建失败: {e}")
        return None, None

def demo_rag_qa(vectorstore, collection_name):
    """演示RAG问答功能"""
    if not vectorstore:
        print("❌ 向量数据库不可用，跳过RAG演示")
        return
    
    print("\n=== RAG问答演示 ===\n")
    
    try:
        # 创建RAG代理
        print("🤖 正在创建RAG代理...")
        rag_agent = RAGAgent(vectorstore, collection_name)
        
        # 显示collection信息
        info = rag_agent.get_collection_info()
        print(f"📊 Collection信息: {info}")
        
        # 演示问题列表
        demo_questions = [
            "这本书的主要内容是什么？",
            "第一章讲了什么内容？",
            "请总结一下关键概念",
            "有什么重要的数据或统计信息？",
            "这本书适合什么人阅读？"
        ]
        
        print(f"\n💬 开始问答演示...")
        print("=" * 60)
        
        for i, question in enumerate(demo_questions, 1):
            print(f"\n🔍 问题 {i}: {question}")
            print("-" * 40)
            
            try:
                # 执行问答
                result = rag_agent.ask(question)
                
                # 显示答案
                print(f"🤖 回答: {result['answer']}")
                print(f"📚 使用了 {result['context_count']} 个相关文档")
                
                # 显示相关文档信息
                if result['context_documents']:
                    print(f"\n📖 相关文档片段:")
                    for j, doc in enumerate(result['context_documents'][:2], 1):
                        metadata = doc['metadata']
                        source = f"{metadata.get('book_name', '未知')} - {metadata.get('chapter', '未知章节')}"
                        content_preview = doc['content'][:100] + "..." if len(doc['content']) > 100 else doc['content']
                        print(f"   {j}. {source}")
                        print(f"      {content_preview}")
                
                print("=" * 60)
                
            except Exception as e:
                print(f"❌ 问答失败: {e}")
                continue
        
        print(f"\n✅ RAG问答演示完成！")
        
    except Exception as e:
        print(f"❌ RAG代理创建失败: {e}")

def demo_retrieval_test(vectorstore):
    """演示检索功能"""
    if not vectorstore:
        return
    
    print("\n=== 检索功能演示 ===\n")
    
    try:
        rag_agent = RAGAgent(vectorstore, "demo_collection")
        
        test_queries = [
            "统计学",
            "流行病学",
            "数据",
            "研究",
            "方法"
        ]
        
        print("🔍 测试检索功能...")
        
        for query in test_queries:
            print(f"\n查询: '{query}'")
            
            # 测试检索
            docs = rag_agent.retrieve_documents(query, top_k=3)
            print(f"找到 {len(docs)} 个相关文档:")
            
            for i, doc in enumerate(docs, 1):
                metadata = doc.metadata
                source = f"{metadata.get('book_name', '未知')} - {metadata.get('chapter', '未知章节')}"
                content_preview = doc.page_content[:80] + "..." if len(doc.page_content) > 80 else doc.page_content
                print(f"  {i}. {source}")
                print(f"     {content_preview}")
        
    except Exception as e:
        print(f"❌ 检索测试失败: {e}")

def main():
    """主演示函数"""
    print("🚀 DT Study Companion RAG系统演示")
    print("=" * 50)
    
    # 1. 演示DOCX处理
    chunks = demo_docx_processing()
    
    if chunks:
        # 2. 演示向量数据库构建
        vectorstore, collection_name = demo_vectorstore_building(chunks)
        
        if vectorstore:
            # 3. 演示RAG问答
            demo_rag_qa(vectorstore, collection_name)
            
            # 4. 演示检索功能
            demo_retrieval_test(vectorstore)
            
            print("\n🎉 演示完成！RAG系统运行正常。")
            print("\n💡 提示:")
            print("   - 运行 'python start_rag_system.py' 启动完整系统")
            print("   - 访问 'frontend/rag_interface.html' 使用Web界面")
            print("   - 运行 'python api/rag_api.py' 启动API服务器")
        else:
            print("\n❌ 向量数据库构建失败，演示终止")
    else:
        print("\n❌ DOCX处理失败，演示终止")

if __name__ == "__main__":
    main()
