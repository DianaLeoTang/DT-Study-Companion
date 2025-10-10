"""LangGraph工作流编排"""
from typing import TypedDict, Annotated, Literal
from langgraph.graph import StateGraph, END
from loguru import logger

from ..agents.query_parser import QueryParserAgent
from ..agents.version_validator import VersionValidatorAgent
from ..agents.retriever import RetrieverAgent
from ..agents.answer_generator import AnswerGeneratorAgent

# ===== 状态定义 =====
class AgentState(TypedDict):
    """Agent工作流状态"""
    # 输入
    query: str  # 用户原始查询
    
    # 解析结果
    book_name: str
    version: str
    question: str
    parse_confidence: float
    
    # 验证结果
    is_valid: bool
    validation_message: str
    collection_name: str
    book_metadata: dict
    
    # 检索结果
    retrieved_docs: list
    
    # 最终输出
    answer: str
    sources: list
    confidence: float
    error: str

# ===== Agent实例 =====
query_parser = QueryParserAgent()
version_validator = VersionValidatorAgent()
retriever = RetrieverAgent()
answer_generator = AnswerGeneratorAgent()

# ===== Agent节点函数 =====
def parse_query_node(state: AgentState) -> AgentState:
    """节点1: 解析查询"""
    logger.info("=" * 60)
    logger.info("步骤1: 解析用户查询")
    logger.info("=" * 60)
    
    query = state["query"]
    
    try:
        result = query_parser.parse(query)
        
        state["book_name"] = result["book_name"]
        state["version"] = result["version"]
        state["question"] = result["question"]
        state["parse_confidence"] = result["confidence"]
        
        logger.info(f"✓ 解析完成:")
        logger.info(f"  - 书名: {state['book_name']}")
        logger.info(f"  - 版本: 第{state['version']}版" if state['version'] else "  - 版本: 未指定")
        logger.info(f"  - 问题: {state['question']}")
        
    except Exception as e:
        logger.error(f"✗ 查询解析失败: {e}")
        state["error"] = f"查询解析失败: {str(e)}"
    
    return state

def validate_version_node(state: AgentState) -> AgentState:
    """节点2: 验证版本"""
    logger.info("=" * 60)
    logger.info("步骤2: 验证书籍和版本")
    logger.info("=" * 60)
    
    book_name = state["book_name"]
    version = state["version"]
    
    try:
        is_valid, message, metadata = version_validator.validate(book_name, version)
        
        state["is_valid"] = is_valid
        state["validation_message"] = message
        state["book_metadata"] = metadata
        
        if is_valid:
            # 如果自动使用了最新版本，更新version字段
            if message and "最新" in message:
                state["version"] = metadata.get("version", version)
            
            # 获取collection名称
            collection_name = version_validator.get_collection_name(
                book_name, 
                state["version"]
            )
            state["collection_name"] = collection_name
            
            logger.info(f"✓ 验证通过:")
            logger.info(f"  - Collection: {collection_name}")
            if message:
                logger.info(f"  - 提示: {message}")
        else:
            logger.warning(f"✗ 验证失败: {message}")
            state["error"] = message
            
    except Exception as e:
        logger.error(f"✗ 版本验证异常: {e}")
        state["is_valid"] = False
        state["error"] = f"版本验证失败: {str(e)}"
    
    return state

def retrieve_docs_node(state: AgentState) -> AgentState:
    """节点3: 检索文档"""
    logger.info("=" * 60)
    logger.info("步骤3: 检索相关文档")
    logger.info("=" * 60)
    
    collection_name = state["collection_name"]
    question = state["question"]
    version = state["version"]
    
    try:
        docs = retriever.retrieve(
            collection_name=collection_name,
            question=question,
            version=version
        )
        
        state["retrieved_docs"] = docs
        
        logger.info(f"✓ 检索完成: 找到 {len(docs)} 个相关文档")
        
        if docs:
            logger.info("  相关度TOP3:")
            for i, doc in enumerate(docs[:3], 1):
                chapter = doc["metadata"].get("chapter", "N/A")
                page = doc["metadata"].get("page", "N/A")
                score = doc.get("score", 0)
                logger.info(f"    {i}. {chapter} 第{page}页 (相似度: {score:.4f})")
        
    except Exception as e:
        logger.error(f"✗ 文档检索失败: {e}")
        state["retrieved_docs"] = []
        state["error"] = f"文档检索失败: {str(e)}"
    
    return state

def generate_answer_node(state: AgentState) -> AgentState:
    """节点4: 生成答案"""
    logger.info("=" * 60)
    logger.info("步骤4: 生成答案")
    logger.info("=" * 60)
    
    question = state["question"]
    retrieved_docs = state["retrieved_docs"]
    book_name = state["book_name"]
    version = state["version"]
    metadata = state["book_metadata"]
    
    try:
        result = answer_generator.generate(
            question=question,
            retrieved_docs=retrieved_docs,
            book_name=book_name,
            version=version,
            metadata=metadata
        )
        
        state["answer"] = result["answer"]
        state["sources"] = result["sources"]
        state["confidence"] = result["confidence"]
        
        logger.info(f"✓ 答案生成完成")
        logger.info(f"  - 置信度: {result['confidence']:.2%}")
        logger.info(f"  - 引用来源: {len(result['sources'])} 处")
        
    except Exception as e:
        logger.error(f"✗ 答案生成失败: {e}")
        state["answer"] = "抱歉，生成答案时出现错误。"
        state["error"] = f"答案生成失败: {str(e)}"
    
    return state

def handle_error_node(state: AgentState) -> AgentState:
    """错误处理节点"""
    error_msg = state.get("error", "未知错误")
    
    # 如果是验证失败，提供书籍列表
    if "系统中没有" in error_msg or "没有第" in error_msg:
        error_msg += "\n\n" + version_validator.list_all_books_and_versions()
    
    state["answer"] = f"❌ {error_msg}"
    state["sources"] = []
    state["confidence"] = 0.0
    
    logger.info("已处理错误并返回提示信息")
    return state

# ===== 路由函数 =====
def should_continue_after_validation(state: AgentState) -> Literal["retrieve", "error"]:
    """判断验证后是否继续"""
    if state.get("error") or not state.get("is_valid"):
        return "error"
    return "retrieve"

def should_continue_after_retrieval(state: AgentState) -> Literal["generate", "error"]:
    """判断检索后是否继续"""
    if state.get("error"):
        return "error"
    # 即使没有检索到文档，也继续生成（生成器会处理这种情况）
    return "generate"

# ===== 构建工作流 =====
def build_workflow():
    """构建LangGraph工作流"""
    workflow = StateGraph(AgentState)
    
    # 添加节点
    workflow.add_node("parse", parse_query_node)
    workflow.add_node("validate", validate_version_node)
    workflow.add_node("retrieve", retrieve_docs_node)
    workflow.add_node("generate", generate_answer_node)
    workflow.add_node("error", handle_error_node)
    
    # 设置入口点
    workflow.set_entry_point("parse")
    
    # 添加边
    workflow.add_edge("parse", "validate")
    
    workflow.add_conditional_edges(
        "validate",
        should_continue_after_validation,
        {
            "retrieve": "retrieve",
            "error": "error"
        }
    )
    
    workflow.add_conditional_edges(
        "retrieve",
        should_continue_after_retrieval,
        {
            "generate": "generate",
            "error": "error"
        }
    )
    
    workflow.add_edge("generate", END)
    workflow.add_edge("error", END)
    
    return workflow.compile()

# ===== 主查询接口 =====
class TextbookAssistant:
    """课本助手主类"""
    
    def __init__(self):
        self.app = build_workflow()
        logger.info("课本助手初始化完成")
    
    def query(self, user_query: str) -> dict:
        """
        处理用户查询
        
        Args:
            user_query: 用户查询
            
        Returns:
            {
                "answer": str,
                "sources": list,
                "confidence": float,
                "book_name": str,
                "version": str
            }
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"新查询: {user_query}")
        logger.info(f"{'='*60}\n")
        
        # 初始化状态
        initial_state = {
            "query": user_query,
            "book_name": "",
            "version": "",
            "question": "",
            "parse_confidence": 0.0,
            "is_valid": False,
            "validation_message": "",
            "collection_name": "",
            "book_metadata": {},
            "retrieved_docs": [],
            "answer": "",
            "sources": [],
            "confidence": 0.0,
            "error": ""
        }
        
        # 执行工作流
        result = self.app.invoke(initial_state)
        
        logger.info(f"\n{'='*60}")
        logger.info("查询处理完成")
        logger.info(f"{'='*60}\n")
        
        return {
            "answer": result["answer"],
            "sources": result["sources"],
            "confidence": result["confidence"],
            "book_name": result["book_name"],
            "version": result["version"],
            "question": result["question"]
        }

# 测试代码
if __name__ == "__main__":
    assistant = TextbookAssistant()
    
    test_queries = [
        "流行病学第7版，什么是队列研究？",
        "生理学第9版中关于心脏的内容",
    ]
    
    for query in test_queries:
        result = assistant.query(query)
        print(f"\n问题: {query}")
        print(f"答案: {result['answer'][:200]}...")
        print(f"置信度: {result['confidence']:.2%}")