"""
配置管理模块 - 现代化配置管理
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger
from typing import Optional

# 加载环境变量
load_dotenv()

class Config:
    """配置类 - 统一管理所有配置项"""
    
    # ===== 应用配置 =====
    APP_NAME = "DT Study Companion"
    APP_VERSION = "2.0.0"
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    
    # ===== API配置 =====
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8000"))
    API_WORKERS = int(os.getenv("API_WORKERS", "4"))
    
    # ===== 数据库配置 =====
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/database/app.db")
    
    # ===== 向量数据库配置 =====
    VECTOR_DB_TYPE = os.getenv("VECTOR_DB_TYPE", "chroma")
    CHROMA_PATH = os.getenv("CHROMA_PATH", "./data/database/chroma_db")
    
    # ===== LLM配置 =====
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
    LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4-turbo-preview")
    
    # OpenAI配置
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    
    # Anthropic配置
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    
    # 阿里通义千问配置
    DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")
    
    # ===== 嵌入模型配置 =====
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-large-zh-v1.5")
    EMBEDDING_DEVICE = os.getenv("EMBEDDING_DEVICE", "cpu")
    EMBEDDING_BATCH_SIZE = int(os.getenv("EMBEDDING_BATCH_SIZE", "32"))
    
    # ===== 文档处理配置 =====
    DOCX_CHUNK_SIZE = int(os.getenv("DOCX_CHUNK_SIZE", "1000"))
    DOCX_CHUNK_OVERLAP = int(os.getenv("DOCX_CHUNK_OVERLAP", "200"))
    PDF_CHUNK_SIZE = int(os.getenv("PDF_CHUNK_SIZE", "1000"))
    PDF_CHUNK_OVERLAP = int(os.getenv("PDF_CHUNK_OVERLAP", "200"))
    
    # ===== 检索配置 =====
    RETRIEVAL_TOP_K = int(os.getenv("RETRIEVAL_TOP_K", "5"))
    RETRIEVAL_SCORE_THRESHOLD = float(os.getenv("RETRIEVAL_SCORE_THRESHOLD", "0.5"))
    
    # ===== 安全配置 =====
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "43200"))
    
    # ===== 文件路径配置 =====
    DATA_DIR = Path(os.getenv("DATA_DIR", "./data"))
    DOCUMENTS_DIR = DATA_DIR / "documents"
    PROCESSED_DIR = DATA_DIR / "processed"
    DATABASE_DIR = DATA_DIR / "database"
    
    # ===== 日志配置 =====
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "./logs/app.log")
    
    @classmethod
    def validate_config(cls) -> bool:
        """验证配置"""
        errors = []
        warnings = []
        
        # 检查必要的目录
        for dir_path in [cls.DATA_DIR, cls.DOCUMENTS_DIR, cls.PROCESSED_DIR, cls.DATABASE_DIR]:
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                errors.append(f"无法创建目录 {dir_path}: {e}")
        
        # 检查LLM配置
        if cls.LLM_PROVIDER == "openai" and not cls.OPENAI_API_KEY:
            warnings.append("OpenAI API密钥未配置，将使用模拟模式")
        elif cls.LLM_PROVIDER == "anthropic" and not cls.ANTHROPIC_API_KEY:
            warnings.append("Anthropic API密钥未配置，将使用模拟模式")
        elif cls.LLM_PROVIDER == "dashscope" and not cls.DASHSCOPE_API_KEY:
            warnings.append("DashScope API密钥未配置，将使用模拟模式")
        
        # 检查安全配置
        if cls.SECRET_KEY == "your-secret-key-here":
            warnings.append("使用默认SECRET_KEY，生产环境请更改")
        
        # 显示警告
        if warnings:
            logger.warning("配置警告:")
            for warning in warnings:
                logger.warning(f"  - {warning}")
        
        # 显示错误
        if errors:
            logger.error("配置错误:")
            for error in errors:
                logger.error(f"  - {error}")
            return False
        
        logger.info("✅ 配置验证通过")
        return True
    
    @classmethod
    def get_llm_config(cls) -> dict:
        """获取LLM配置"""
        config = {
            "provider": cls.LLM_PROVIDER,
            "model": cls.LLM_MODEL
        }
        
        if cls.LLM_PROVIDER == "openai":
            config.update({
                "api_key": cls.OPENAI_API_KEY,
                "base_url": cls.OPENAI_BASE_URL
            })
        elif cls.LLM_PROVIDER == "anthropic":
            config.update({
                "api_key": cls.ANTHROPIC_API_KEY
            })
        elif cls.LLM_PROVIDER == "dashscope":
            config.update({
                "api_key": cls.DASHSCOPE_API_KEY
            })
        
        return config
    
    @classmethod
    def get_embedding_config(cls) -> dict:
        """获取嵌入模型配置"""
        return {
            "model": cls.EMBEDDING_MODEL,
            "device": cls.EMBEDDING_DEVICE,
            "batch_size": cls.EMBEDDING_BATCH_SIZE
        }
    
    @classmethod
    def get_vector_db_config(cls) -> dict:
        """获取向量数据库配置"""
        config = {
            "type": cls.VECTOR_DB_TYPE
        }
        
        if cls.VECTOR_DB_TYPE == "chroma":
            config.update({
                "path": cls.CHROMA_PATH
            })
        
        return config

# 创建全局配置实例
config = Config()