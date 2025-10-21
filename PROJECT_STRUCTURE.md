# DT Study Companion - 项目结构设计

## 🏗️ 新的专业项目结构

```
dt-study-companion/
├── 📁 backend/                    # 后端服务
│   ├── 📁 app/                    # 应用核心
│   │   ├── 📁 api/               # API路由
│   │   │   ├── __init__.py
│   │   │   ├── auth.py           # 认证相关
│   │   │   ├── documents.py      # 文档管理
│   │   │   ├── queries.py        # 查询接口
│   │   │   └── health.py         # 健康检查
│   │   ├── 📁 core/              # 核心业务逻辑
│   │   │   ├── __init__.py
│   │   │   ├── config.py         # 配置管理
│   │   │   ├── database.py       # 数据库连接
│   │   │   └── security.py       # 安全相关
│   │   ├── 📁 models/            # 数据模型
│   │   │   ├── __init__.py
│   │   │   ├── user.py           # 用户模型
│   │   │   ├── document.py        # 文档模型
│   │   │   └── query.py          # 查询模型
│   │   ├── 📁 services/          # 业务服务
│   │   │   ├── __init__.py
│   │   │   ├── rag_service.py    # RAG服务
│   │   │   ├── document_service.py # 文档服务
│   │   │   └── user_service.py   # 用户服务
│   │   ├── 📁 utils/             # 工具函数
│   │   │   ├── __init__.py
│   │   │   ├── logger.py         # 日志工具
│   │   │   └── helpers.py        # 辅助函数
│   │   └── main.py               # 应用入口
│   ├── 📁 rag/                   # RAG核心模块
│   │   ├── __init__.py
│   │   ├── 📁 agents/            # RAG代理
│   │   │   ├── __init__.py
│   │   │   ├── query_agent.py    # 查询代理
│   │   │   ├── retrieval_agent.py # 检索代理
│   │   │   └── generation_agent.py # 生成代理
│   │   ├── 📁 preprocessing/     # 文档预处理
│   │   │   ├── __init__.py
│   │   │   ├── docx_parser.py    # DOCX解析
│   │   │   ├── pdf_parser.py     # PDF解析
│   │   │   └── text_processor.py # 文本处理
│   │   ├── 📁 vectorstore/       # 向量存储
│   │   │   ├── __init__.py
│   │   │   ├── chroma_client.py  # ChromaDB客户端
│   │   │   └── embeddings.py     # 嵌入模型
│   │   └── 📁 llm/               # 大语言模型
│   │       ├── __init__.py
│   │       ├── openai_client.py  # OpenAI客户端
│   │       ├── anthropic_client.py # Anthropic客户端
│   │       └── base_client.py    # 基础客户端
│   ├── 📁 database/              # 数据库相关
│   │   ├── __init__.py
│   │   ├── migrations/           # 数据库迁移
│   │   └── init_db.py           # 数据库初始化
│   ├── 📁 tests/                 # 测试文件
│   │   ├── __init__.py
│   │   ├── test_api.py          # API测试
│   │   ├── test_rag.py          # RAG测试
│   │   └── test_utils.py        # 工具测试
│   ├── requirements.txt          # 后端依赖
│   └── Dockerfile               # Docker配置
├── 📁 frontend/                  # 前端应用
│   ├── 📁 public/               # 静态资源
│   │   ├── index.html
│   │   ├── favicon.ico
│   │   └── assets/
│   ├── 📁 src/                   # 源代码
│   │   ├── 📁 components/       # React组件
│   │   │   ├── 📁 common/       # 通用组件
│   │   │   │   ├── Header.jsx
│   │   │   │   ├── Footer.jsx
│   │   │   │   └── Loading.jsx
│   │   │   ├── 📁 query/        # 查询相关组件
│   │   │   │   ├── QueryForm.jsx
│   │   │   │   ├── QueryResults.jsx
│   │   │   │   └── DocumentList.jsx
│   │   │   └── 📁 document/     # 文档相关组件
│   │   │       ├── DocumentUpload.jsx
│   │   │       └── DocumentList.jsx
│   │   ├── 📁 services/         # API服务
│   │   │   ├── api.js           # API客户端
│   │   │   ├── auth.js          # 认证服务
│   │   │   └── document.js      # 文档服务
│   │   ├── 📁 utils/            # 工具函数
│   │   │   ├── constants.js     # 常量
│   │   │   └── helpers.js       # 辅助函数
│   │   ├── 📁 styles/           # 样式文件
│   │   │   ├── globals.css
│   │   │   └── components.css
│   │   ├── App.jsx              # 主应用组件
│   │   └── index.js             # 入口文件
│   ├── package.json             # 前端依赖
│   ├── vite.config.js           # Vite配置
│   └── Dockerfile               # Docker配置
├── 📁 data/                     # 数据目录
│   ├── 📁 documents/           # 原始文档
│   │   ├── 📁 pdfs/            # PDF文件
│   │   ├── 📁 docx/            # DOCX文件
│   │   └── 📁 metadata/        # 元数据
│   ├── 📁 processed/           # 处理后的数据
│   │   ├── 📁 chunks/          # 文本块
│   │   └── 📁 vectors/         # 向量数据
│   └── 📁 database/            # 数据库文件
│       └── chroma_db/          # ChromaDB存储
├── 📁 scripts/                  # 脚本文件
│   ├── setup.sh               # 环境设置
│   ├── start_backend.sh        # 启动后端
│   ├── start_frontend.sh       # 启动前端
│   └── process_documents.py    # 文档处理
├── 📁 docs/                    # 文档
│   ├── API.md                  # API文档
│   ├── DEPLOYMENT.md           # 部署文档
│   └── DEVELOPMENT.md          # 开发文档
├── 📁 docker/                  # Docker配置
│   ├── docker-compose.yml      # 容器编排
│   ├── docker-compose.dev.yml  # 开发环境
│   └── docker-compose.prod.yml # 生产环境
├── .env.example                # 环境变量示例
├── .gitignore                  # Git忽略文件
├── README.md                   # 项目说明
└── docker-compose.yml          # 主Docker配置
```

## 🎯 架构设计原则

### 1. **前后端分离**
- **后端**: FastAPI + Python，提供RESTful API
- **前端**: React + Vite，现代化用户界面
- **通信**: HTTP/JSON，标准RESTful接口

### 2. **模块化设计**
- **RAG模块**: 独立的检索增强生成逻辑
- **API模块**: 清晰的接口层
- **数据模块**: 统一的数据管理

### 3. **可扩展性**
- **微服务架构**: 各模块独立部署
- **插件化**: 支持新的文档类型和LLM
- **配置化**: 通过配置文件管理参数

## 🚀 技术栈

### 后端技术栈
- **框架**: FastAPI
- **数据库**: SQLite/PostgreSQL + ChromaDB
- **RAG**: LangChain + ChromaDB
- **LLM**: OpenAI/Anthropic/本地模型
- **部署**: Docker + Docker Compose

### 前端技术栈
- **框架**: React 18
- **构建工具**: Vite
- **UI库**: Ant Design / Material-UI
- **状态管理**: Zustand / Redux Toolkit
- **HTTP客户端**: Axios

## 📋 迁移计划

1. **第一阶段**: 重新组织后端代码
2. **第二阶段**: 创建现代化前端
3. **第三阶段**: 完善文档和部署
4. **第四阶段**: 测试和优化

## 🔧 开发工具

- **代码格式化**: Black + Prettier
- **类型检查**: mypy + TypeScript
- **测试**: pytest + Jest
- **文档**: Sphinx + Storybook
- **CI/CD**: GitHub Actions
