# DT Study Companion - 现代化RAG问答系统

## 🎯 项目简介

DT Study Companion 是一个基于RAG（检索增强生成）技术的智能医学问答系统，采用现代化的前后端分离架构，为医学学习提供智能化的文档问答服务。

## 🏗️ 系统架构

### 技术栈
- **后端**: FastAPI + Python 3.8+
- **前端**: HTML5 + CSS3 + JavaScript (ES6+)
- **数据库**: SQLite + ChromaDB
- **RAG引擎**: LangChain + ChromaDB
- **LLM**: OpenAI / Anthropic / 本地模型

### 架构特点
- ✅ **前后端分离**: 清晰的API接口设计
- ✅ **模块化设计**: 可扩展的组件架构
- ✅ **现代化UI**: 响应式用户界面
- ✅ **RESTful API**: 标准化的接口设计
- ✅ **容器化部署**: Docker支持

## 📁 项目结构

```
dt-study-companion/
├── 📁 backend/                    # 后端服务
│   ├── 📁 app/                    # 应用核心
│   │   ├── 📁 api/               # API路由
│   │   │   ├── auth.py          # 认证接口
│   │   │   ├── documents.py     # 文档管理
│   │   │   ├── queries.py       # 查询接口
│   │   │   └── health.py        # 健康检查
│   │   ├── 📁 core/              # 核心配置
│   │   │   └── config.py        # 配置管理
│   │   ├── 📁 models/            # 数据模型
│   │   ├── 📁 services/          # 业务服务
│   │   └── main.py              # 应用入口
│   ├── 📁 rag/                   # RAG核心模块
│   │   ├── 📁 agents/           # RAG代理
│   │   ├── 📁 preprocessing/    # 文档预处理
│   │   ├── 📁 vectorstore/     # 向量存储
│   │   └── 📁 llm/             # 大语言模型
│   └── requirements.txt         # 后端依赖
├── 📁 frontend/                 # 前端应用
│   └── 📁 public/               # 静态资源
│       └── index.html           # 主页面
├── 📁 data/                     # 数据目录
│   ├── 📁 documents/            # 原始文档
│   ├── 📁 processed/           # 处理后的数据
│   └── 📁 database/            # 数据库文件
├── 📁 scripts/                  # 脚本文件
├── 📁 docs/                    # 文档
└── start_new_system.py         # 新系统启动脚本
```

## 🚀 快速开始

### 1. 环境要求
- Python 3.8+
- pip 包管理器
- 现代浏览器

### 2. 安装依赖
```bash
# 安装Python依赖
pip install -r backend/requirements.txt --break-system-packages
```

### 3. 启动系统
```bash
# 一键启动新系统
python start_new_system.py
```

### 4. 访问系统
- **前端界面**: http://localhost:8000
- **API文档**: http://localhost:8000/api/docs
- **健康检查**: http://localhost:8000/api/health

## 🔧 开发指南

### 后端开发
```bash
# 启动后端服务
cd backend
python app/main.py

# 或使用uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 前端开发
```bash
# 前端文件位于 frontend/public/
# 可以直接编辑 HTML/CSS/JavaScript
# 支持热重载（通过后端服务）
```

### API接口
```bash
# 查看所有API接口
curl http://localhost:8000/api/docs

# 健康检查
curl http://localhost:8000/api/health

# 查询问答
curl -X POST http://localhost:8000/api/queries/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "什么是卫生统计学？"}'
```

## 📚 功能特性

### 🧠 智能问答
- **语义检索**: 基于向量相似度的文档检索
- **上下文理解**: 智能构建问答上下文
- **多文档支持**: 支持多种医学文档类型
- **实时问答**: 毫秒级响应速度

### 📄 文档管理
- **多格式支持**: DOCX、PDF等格式
- **智能解析**: 自动提取文本和结构
- **批量处理**: 支持批量文档上传
- **版本管理**: 文档版本控制

### 🎨 用户界面
- **现代化设计**: 响应式用户界面
- **实时交互**: 流畅的用户体验
- **多设备支持**: 桌面和移动端适配
- **主题定制**: 可定制的界面主题

## 🔧 配置说明

### 环境变量
```bash
# API配置
API_HOST=0.0.0.0
API_PORT=8000

# 数据库配置
DATABASE_URL=sqlite:///./data/database/app.db

# LLM配置
LLM_PROVIDER=openai
OPENAI_API_KEY=your_api_key_here

# 向量数据库
CHROMA_PATH=./data/database/chroma_db
```

### 配置文件
- `backend/app/core/config.py`: 主配置文件
- `.env.example`: 环境变量示例

## 🐳 Docker部署

### 构建镜像
```bash
# 构建后端镜像
docker build -t dt-study-companion-backend ./backend

# 构建前端镜像
docker build -t dt-study-companion-frontend ./frontend
```

### 运行容器
```bash
# 使用docker-compose
docker-compose up -d

# 或单独运行
docker run -p 8000:8000 dt-study-companion-backend
```

## 🧪 测试

### 运行测试
```bash
# 后端测试
cd backend
python -m pytest tests/

# API测试
curl http://localhost:8000/api/health
```

### 性能测试
```bash
# 使用ab进行压力测试
ab -n 100 -c 10 http://localhost:8000/api/health
```

## 📈 监控和日志

### 日志配置
- **日志级别**: INFO/DEBUG/ERROR
- **日志文件**: `logs/app.log`
- **日志格式**: 结构化JSON格式

### 监控指标
- **API响应时间**: 平均响应时间监控
- **错误率**: API错误率统计
- **资源使用**: CPU/内存使用情况

## 🔒 安全考虑

### API安全
- **CORS配置**: 跨域请求控制
- **请求限制**: 防止API滥用
- **输入验证**: 严格的输入参数验证

### 数据安全
- **数据加密**: 敏感数据加密存储
- **访问控制**: 基于角色的访问控制
- **审计日志**: 完整的操作审计

## 🤝 贡献指南

### 开发流程
1. Fork 项目
2. 创建功能分支
3. 提交代码
4. 创建 Pull Request

### 代码规范
- **Python**: 遵循PEP 8规范
- **JavaScript**: 使用ES6+语法
- **文档**: 完整的API文档

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

感谢所有为这个项目做出贡献的开发者和用户！

---

**DT Study Companion** - 让医学学习更智能 🚀
