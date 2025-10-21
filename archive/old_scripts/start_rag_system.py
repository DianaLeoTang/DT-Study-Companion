#!/usr/bin/env python3
"""启动RAG系统"""
import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path
from loguru import logger

def setup_logging():
    """设置日志"""
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level="INFO"
    )

def check_dependencies():
    """检查依赖"""
    logger.info("检查依赖...")
    
    required_packages = [
        "fastapi",
        "uvicorn", 
        "docx",  # python-docx的导入名是docx
        "langchain",
        "chromadb",
        "sentence_transformers"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        logger.warning(f"缺少依赖包: {', '.join(missing_packages)}")
        logger.info("尝试自动安装依赖...")
        
        # 尝试自动安装
        try:
            import subprocess
            import sys
            
            for package in missing_packages:
                if package == "docx":
                    package_name = "python-docx"
                else:
                    package_name = package
                
                logger.info(f"正在安装 {package_name}...")
                result = subprocess.run([
                    sys.executable, "-m", "pip", "install", package_name, "--break-system-packages"
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    logger.info(f"✓ {package_name} 安装成功")
                else:
                    logger.error(f"✗ {package_name} 安装失败: {result.stderr}")
            
            # 重新检查依赖
            missing_packages = []
            for package in required_packages:
                try:
                    __import__(package)
                except ImportError:
                    missing_packages.append(package)
            
            if missing_packages:
                logger.error(f"仍有依赖包未安装: {', '.join(missing_packages)}")
                logger.info("请手动运行: pip install -r requirement.txt --break-system-packages")
                return False
                
        except Exception as e:
            logger.error(f"自动安装失败: {e}")
            logger.info("请手动运行: pip install -r requirement.txt --break-system-packages")
            return False
    
    logger.info("✓ 依赖检查通过")
    return True

def process_documents():
    """处理文档"""
    logger.info("开始处理DOCX文档...")
    
    try:
        # 直接导入并运行文档处理逻辑
        from src.preprocessing.docx_parser import DOCXParser
        from src.preprocessing.vectorstore_builder import VectorStoreBuilder
        from src.utils.config import Config
        import json
        
        # 查找DOCX文件
        data_dir = Path("data")
        docx_files = list(data_dir.glob("*.docx"))
        
        if not docx_files:
            logger.warning("未找到DOCX文件，跳过文档处理")
            return True
        
        logger.info(f"找到 {len(docx_files)} 个DOCX文件")
        
        # 处理所有DOCX文件
        all_chunks = {}
        parser = DOCXParser()
        
        for i, file in enumerate(docx_files):
            logger.info(f"处理文件 {i+1}/{len(docx_files)}: {file.name}")
            
            try:
                chunks = parser.parse_docx(str(file))
                
                # 添加元数据
                for chunk in chunks:
                    chunk["metadata"]["book_id"] = f"book_{i+1}"
                    chunk["metadata"]["book_name"] = file.stem
                    chunk["metadata"]["version"] = "1"
                    chunk["metadata"]["filename"] = file.name
                    chunk["metadata"]["file_type"] = "docx"
                
                # 清理文件名，确保符合ChromaDB collection名称规范
                clean_name = file.stem
                # 移除特殊字符，只保留字母、数字、下划线和连字符
                import re
                clean_name = re.sub(r'[^\w\-]', '_', clean_name)
                # 确保以字母或数字开头和结尾
                clean_name = re.sub(r'^[^a-zA-Z0-9]+', '', clean_name)
                clean_name = re.sub(r'[^a-zA-Z0-9]+$', '', clean_name)
                # 限制长度
                clean_name = clean_name[:50]
                collection_name = f"docx_{clean_name}"
                all_chunks[collection_name] = chunks
                
                logger.info(f"✓ {file.name} 处理完成: {len(chunks)} 个文本块")
                
            except Exception as e:
                logger.error(f"✗ {file.name} 处理失败: {e}")
                continue
        
        if all_chunks:
            # 构建向量数据库
            logger.info("构建向量数据库...")
            builder = VectorStoreBuilder()
            builder.build_all_collections(all_chunks, force_rebuild=True)
            logger.info("✓ 向量数据库构建完成")
            
            # 保存处理摘要
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
            
            # 确保输出目录存在
            output_dir = Path("data/processed")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            with open("data/processed/docx_processing_summary.json", 'w', encoding='utf-8') as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)
            
            logger.info("✓ 文档处理完成")
            return True
        else:
            logger.warning("没有成功处理任何文档")
            return False
            
    except Exception as e:
        logger.error(f"文档处理异常: {e}")
        return False

def start_api_server():
    """启动API服务器"""
    logger.info("启动RAG API服务器...")
    
    try:
        # 检查端口是否被占用
        import socket
        def is_port_in_use(port):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                return s.connect_ex(('localhost', port)) == 0
        
        # 尝试不同的端口
        ports_to_try = [8000, 8001, 8002, 8003, 8004]
        selected_port = None
        
        for port in ports_to_try:
            if not is_port_in_use(port):
                selected_port = port
                break
        
        if selected_port is None:
            logger.error("所有端口都被占用，无法启动API服务器")
            return None
        
        logger.info(f"使用端口 {selected_port} 启动API服务器")
        
        # 设置环境变量指定端口
        import os
        env = os.environ.copy()
        env['API_PORT'] = str(selected_port)
        
        # 启动API服务器
        api_process = subprocess.Popen([
            sys.executable, "api/rag_api.py"
        ], cwd=Path(__file__).parent, env=env)
        
        # 等待服务器启动
        time.sleep(5)
        
        # 检查服务器是否运行
        import requests
        try:
            response = requests.get(f"http://localhost:{selected_port}/health", timeout=5)
            if response.status_code == 200:
                logger.info(f"✓ RAG API服务器启动成功，端口: {selected_port}")
                return api_process, selected_port
            else:
                logger.error("API服务器响应异常")
                return None, None
        except requests.exceptions.RequestException:
            logger.error("无法连接到API服务器")
            return None, None
            
    except Exception as e:
        logger.error(f"启动API服务器失败: {e}")
        return None, None

def open_web_interface():
    """打开Web界面"""
    logger.info("打开Web界面...")
    
    try:
        interface_path = Path(__file__).parent / "frontend" / "rag_interface.html"
        webbrowser.open(f"file://{interface_path.absolute()}")
        logger.info("✓ Web界面已打开")
    except Exception as e:
        logger.error(f"打开Web界面失败: {e}")

def main():
    """主函数"""
    setup_logging()
    
    logger.info("=== DT Study Companion RAG系统启动 ===")
    
    # 1. 检查依赖
    if not check_dependencies():
        return 1
    
    # 2. 处理文档
    if not process_documents():
        logger.warning("文档处理失败，但继续启动API服务器")
    
    # 3. 启动API服务器
    result = start_api_server()
    if result is None or result[0] is None:
        logger.error("API服务器启动失败")
        return 1
    
    api_process, port = result
    
    # 4. 打开Web界面
    open_web_interface()
    
    logger.info("=== RAG系统启动完成 ===")
    logger.info(f"API服务器: http://localhost:{port}")
    logger.info("Web界面: frontend/rag_interface.html")
    logger.info("按 Ctrl+C 停止服务器")
    
    try:
        # 保持服务器运行
        api_process.wait()
    except KeyboardInterrupt:
        logger.info("正在停止服务器...")
        api_process.terminate()
        api_process.wait()
        logger.info("服务器已停止")
    
    return 0

if __name__ == "__main__":
    exit(main())
