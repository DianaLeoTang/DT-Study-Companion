"""配置管理模块"""
import os
from dotenv import load_dotenv
from loguru import logger

# 加载环境变量
load_dotenv()

class Config:
    """配置类"""
    
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
    
    # ===== Embedding配置 =====
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-large-zh-v1.5")
    EMBEDDING_DEVICE = os.getenv("EMBEDDING_DEVICE", "cpu")
    EMBEDDING_BATCH_SIZE = int(os.getenv("EMBEDDING_BATCH_SIZE", "32"))
    
    # ===== 向量数据库配置 =====
    VECTOR_DB = os.getenv("VECTOR_DB", "chroma")
    CHROMA_PATH = os.getenv("CHROMA_PATH", "./database/chroma_db")
    
    # Qdrant配置
    QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
    QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
    
    # ===== 文档处理配置 =====
    PDF_CHUNK_SIZE = int(os.getenv("PDF_CHUNK_SIZE", "1000"))
    PDF_CHUNK_OVERLAP = int(os.getenv("PDF_CHUNK_OVERLAP", "200"))
    DOCX_CHUNK_SIZE = int(os.getenv("DOCX_CHUNK_SIZE", "1000"))
    DOCX_CHUNK_OVERLAP = int(os.getenv("DOCX_CHUNK_OVERLAP", "200"))
    
    # ===== 检索配置 =====
    RETRIEVAL_TOP_K = int(os.getenv("RETRIEVAL_TOP_K", "5"))
    RETRIEVAL_SCORE_THRESHOLD = float(os.getenv("RETRIEVAL_SCORE_THRESHOLD", "0.5"))
    
    # ===== API配置 =====
    API_PORT = int(os.getenv("API_PORT", "8000"))
    API_WORKERS = int(os.getenv("API_WORKERS", "4"))
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    
    # ===== 数据库配置 =====
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dt_study_companion.db")
    
    # ===== 认证配置 =====
    SECRET_KEY = os.getenv("SECRET_KEY", "")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "43200"))  # 30天
    
    # ===== Redis配置 =====
    REDIS_ENABLED = os.getenv("REDIS_ENABLED", "false").lower() == "true"
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB = int(os.getenv("REDIS_DB", "0"))
    
    # ===== 日志配置 =====
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", f"./logs/app_{os.getenv('LOG_DATE', '')}.log")
    
    # ===== 文件路径配置 =====
    DATA_DIR = os.getenv("DATA_DIR", "./data")
    RAW_PDFS_DIR = DATA_DIR  # 文档文件直接放在data目录下
    PROCESSED_DIR = os.path.join(DATA_DIR, "processed")
    BOOKS_METADATA_FILE = os.path.join(DATA_DIR, "books_metadata.json")
    
    @classmethod
    def validate_config(cls):
        """验证配置"""
        errors = []
        warnings = []
        
        # 检查LLM配置
        if cls.LLM_PROVIDER == "openai" and not cls.OPENAI_API_KEY:
            warnings.append("OpenAI API密钥未配置，将使用模拟模式")
        elif cls.LLM_PROVIDER == "anthropic" and not cls.ANTHROPIC_API_KEY:
            warnings.append("Anthropic API密钥未配置，将使用模拟模式")
        elif cls.LLM_PROVIDER == "dashscope" and not cls.DASHSCOPE_API_KEY:
            warnings.append("DashScope API密钥未配置，将使用模拟模式")
        
        # 检查认证配置
        if not cls.SECRET_KEY:
            warnings.append("SECRET_KEY未配置，将使用默认值")
            cls.SECRET_KEY = "default_secret_key_for_demo"
        
        # 检查数据目录
        if not os.path.exists(cls.DATA_DIR):
            try:
                os.makedirs(cls.DATA_DIR, exist_ok=True)
            except Exception as e:
                errors.append(f"无法创建数据目录: {e}")
        
        # 显示警告
        if warnings:
            logger.warning("配置警告:")
            for warning in warnings:
                logger.warning(f"  - {warning}")
        
        if errors:
            logger.error("配置验证失败:")
            for error in errors:
                logger.error(f"  - {error}")
            return False
        
        logger.info("配置验证通过")
        return True
    
    @classmethod
    def get_llm_config(cls):
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
    def get_embedding_config(cls):
        """获取Embedding配置"""
        return {
            "model": cls.EMBEDDING_MODEL,
            "device": cls.EMBEDDING_DEVICE,
            "batch_size": cls.EMBEDDING_BATCH_SIZE
        }
    
    @classmethod
    def get_vector_db_config(cls):
        """获取向量数据库配置"""
        config = {
            "type": cls.VECTOR_DB
        }
        
        if cls.VECTOR_DB == "chroma":
            config.update({
                "path": cls.CHROMA_PATH
            })
        elif cls.VECTOR_DB == "qdrant":
            config.update({
                "host": cls.QDRANT_HOST,
                "port": cls.QDRANT_PORT
            })
        
        return config
    
    @classmethod
    def get_redis_config(cls):
        """获取Redis配置"""
        return {
            "enabled": cls.REDIS_ENABLED,
            "host": cls.REDIS_HOST,
            "port": cls.REDIS_PORT,
            "db": cls.REDIS_DB
        }
    
    @classmethod
    def load_books_metadata(cls):
        """加载书籍元数据"""
        import json
        
        try:
            with open(cls.BOOKS_METADATA_FILE, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            logger.info(f"成功加载书籍元数据: {len(metadata.get('books', []))} 本书")
            return metadata
        except FileNotFoundError:
            logger.error(f"书籍元数据文件不存在: {cls.BOOKS_METADATA_FILE}")
            return {"books": []}
        except json.JSONDecodeError as e:
            logger.error(f"书籍元数据文件格式错误: {e}")
            return {"books": []}
        except Exception as e:
            logger.error(f"加载书籍元数据失败: {e}")
            return {"books": []}

# 验证配置
if __name__ == "__main__":
    Config.validate_config()
    
    print("LLM配置:", Config.get_llm_config())
    print("Embedding配置:", Config.get_embedding_config())
    print("向量数据库配置:", Config.get_vector_db_config())
    print("Redis配置:", Config.get_redis_config())
