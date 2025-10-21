# DT Study Companion - RAG问答系统

基于DOCX文档的智能问答系统，支持文档解析、向量化存储和RAG问答。

## 功能特性

- 📄 **DOCX文档解析**: 支持解析Word文档，提取文本和表格内容
- 🔍 **智能分块**: 自动识别章节结构，智能分割文本块
- 🧠 **向量化存储**: 使用ChromaDB存储文档向量，支持快速检索
- 💬 **RAG问答**: 基于检索增强生成的智能问答
- 🌐 **Web界面**: 提供友好的Web界面进行交互
- 🔌 **API接口**: 提供RESTful API供其他系统调用

## 系统架构

```
DOCX文件 → 文档解析器 → 文本分块 → 向量化 → 向量数据库
                                                    ↓
用户问题 → 查询解析 → 向量检索 → 上下文构建 → LLM生成 → 答案返回
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirement.txt
```

### 2. 准备文档

将DOCX文件放入 `data/` 目录：

```
data/
├── 卫生统计学第八版.docx
├── 流行病学第九版吕筠.docx
├── 社会医学.张拓红第二版.docx
└── ...
```

### 3. 启动系统

#### 方式一：一键启动（推荐）

```bash
python start_rag_system.py
```

这将自动：
- 检查依赖
- 处理DOCX文档
- 启动API服务器
- 打开Web界面

#### 方式二：分步启动

1. **处理文档**：
```bash
python scripts/process_documents.py --input data --type docx
```

2. **启动API服务器**：
```bash
python api/rag_api.py
```

3. **打开Web界面**：
在浏览器中打开 `frontend/rag_interface.html`

### 4. 使用系统

访问Web界面：`http://localhost:8000` 或打开 `frontend/rag_interface.html`

## API使用

### 查询文档

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "什么是卫生统计学？",
    "collection_name": "test_collection",
    "use_scores": true,
    "top_k": 5
  }'
```

### 获取可用集合

```bash
curl "http://localhost:8000/collections"
```

### 健康检查

```bash
curl "http://localhost:8000/health"
```

## 配置说明

在 `src/utils/config.py` 中可以配置：

- **文档处理**：
  - `DOCX_CHUNK_SIZE`: DOCX文本块大小（默认1000）
  - `DOCX_CHUNK_OVERLAP`: 文本块重叠大小（默认200）

- **检索配置**：
  - `RETRIEVAL_TOP_K`: 检索文档数量（默认5）
  - `RETRIEVAL_SCORE_THRESHOLD`: 相似度阈值（默认0.5）

- **向量数据库**：
  - `CHROMA_PATH`: ChromaDB存储路径
  - `EMBEDDING_MODEL`: 嵌入模型

## 文件结构

```
├── src/
│   ├── preprocessing/
│   │   ├── docx_parser.py      # DOCX解析器
│   │   └── vectorstore_builder.py  # 向量数据库构建器
│   ├── agents/
│   │   └── rag_agent.py        # RAG问答代理
│   └── utils/
│       ├── config.py           # 配置管理
│       └── llm_client.py       # LLM客户端
├── api/
│   └── rag_api.py              # API接口
├── frontend/
│   └── rag_interface.html      # Web界面
├── scripts/
│   └── process_documents.py    # 文档处理脚本
├── data/                       # 文档存储目录
├── database/chroma_db/         # 向量数据库存储
└── start_rag_system.py         # 系统启动脚本
```

## 使用示例

### 1. 基本问答

**问题**: "什么是卫生统计学？"
**回答**: 基于文档内容生成的专业回答，包含相关章节引用。

### 2. 多文档检索

系统会自动从多个文档中检索相关信息，提供综合答案。

### 3. 上下文感知

系统能够理解章节结构，提供更准确的上下文信息。

## 故障排除

### 1. 依赖安装问题

```bash
# 如果遇到依赖冲突，建议使用虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

pip install -r requirement.txt
```

### 2. 文档解析失败

- 检查DOCX文件是否损坏
- 确保文件编码正确
- 查看日志中的具体错误信息

### 3. 向量数据库问题

- 删除 `database/chroma_db/` 目录重新构建
- 检查磁盘空间是否充足
- 确保有足够的权限写入数据库目录

### 4. API连接问题

- 检查端口8000是否被占用
- 确认防火墙设置
- 查看API服务器日志

## 开发说明

### 添加新的文档类型

1. 在 `src/preprocessing/` 中创建新的解析器
2. 继承基础解析器接口
3. 在 `scripts/process_documents.py` 中集成

### 自定义RAG流程

1. 修改 `src/agents/rag_agent.py`
2. 调整检索策略
3. 自定义提示词模板

### 扩展API功能

1. 在 `api/rag_api.py` 中添加新的端点
2. 定义请求/响应模型
3. 更新Web界面

## 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 贡献

欢迎提交Issue和Pull Request来改进项目。

## 联系方式

如有问题，请通过以下方式联系：
- 提交GitHub Issue
- 发送邮件至项目维护者
