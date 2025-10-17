<!--
 * @Author: Diana Tang
-->
# DT-Study-Companion

**公共卫生学专业AI助教，为你的专业学习之路提供温度与智慧的陪伴。**

一个基于多Agent架构的智能公共卫生学问答系统，支持用户认证、专业领域选择和精准的教材问答。

## ✨ 核心特性

- 🔐 **用户认证系统** - 手机号快速登录，JWT安全认证
- 🎯 **专业领域选择** - 6大公共卫生学专业领域
- 🤖 **多Agent协作** - 智能查询解析、版本验证、文档检索、答案生成
- 📚 **精准问答** - 基于向量数据库的智能检索和回答
- 💻 **现代化界面** - 响应式Web界面，支持移动端
- 📊 **查询历史** - 完整的用户学习记录

## 🎓 专业领域

系统支持以下6大公共卫生学专业领域：

- 🦠 **流行病学** - 疾病分布、病因研究、疾病监测与预防
- 📊 **卫生统计学** - 医学统计方法、数据分析、研究设计
- 🏘️ **社会医学** - 社会因素与健康、卫生政策、社区卫生
- 🏭 **职业卫生学** - 职业危害、职业病防治、工作环境健康
- 🌍 **环境卫生学** - 环境因素与健康、环境污染、环境监测
- 🍎 **营养与食品卫生学** - 营养学基础、食品安全、膳食指导

## 📁 项目结构

```
DT-Study-Companion/
├── api/                          # FastAPI后端服务
│   ├── models.py                 # 数据库模型
│   ├── database.py               # 数据库连接管理
│   ├── auth.py                   # 用户认证模块
│   ├── main.py                   # 主API服务
│   ├── schemas.py                # API数据模型
│   └── services/                 # 业务服务层
│       ├── user_service.py       # 用户服务
│       └── agent_service.py      # Agent服务
├── src/                          # 核心业务逻辑
│   ├── agents/                   # Agent模块
│   │   ├── query_parser.py       # 查询解析Agent
│   │   ├── version_validator.py  # 版本验证Agent
│   │   ├── retriever.py          # 检索Agent
│   │   └── answer_generator.py   # 答案生成Agent
│   ├── preprocessing/            # 数据预处理
│   │   ├── pdf_parser.py         # PDF解析器
│   │   └── vectorstore_builder.py # 向量数据库构建
│   ├── workflow/                 # 工作流编排
│   │   └── agent_graph.py        # LangGraph工作流
│   └── utils/                    # 工具模块
│       ├── config.py             # 配置管理
│       └── llm_client.py         # LLM客户端
├── frontend/                     # 前端界面
│   └── index.html                # 现代化Web界面
├── data/                         # 数据目录
│   └── books_metadata.json       # 书籍元数据
├── scripts/                      # 脚本工具
│   ├── start_server.py           # 启动脚本
│   ├── test_system.py            # 系统测试
│   └── quick_start.sh            # 快速启动
├── requirement.txt               # Python依赖
├── env.example                   # 环境变量示例
├── run_simple.py                 # 简化启动脚本
└── .gitignore                    # Git忽略文件
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd DT-Study-Companion

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirement.txt
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp env.example .env

# 编辑.env文件，配置以下关键参数：
# - OPENAI_API_KEY=your-openai-api-key
# - SECRET_KEY=your-secret-key
```

### 3. 启动服务

```bash
# 方式1: 使用简化启动脚本（推荐）
python3 run_simple.py

# 方式2: 使用完整启动脚本
python3 scripts/start_server.py

# 方式3: 使用Shell脚本（Linux/macOS）
chmod +x scripts/quick_start.sh
./scripts/quick_start.sh
```

### 4. 访问系统

- **API服务**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **前端界面**: 打开 `frontend/index.html` 文件

## 🛠️ 技术架构

### 后端技术栈
- **FastAPI** - 现代Python Web框架
- **SQLAlchemy** - ORM数据库操作
- **LangChain** - LLM应用开发框架
- **LangGraph** - 多Agent工作流编排
- **ChromaDB** - 向量数据库
- **JWT** - 用户认证
- **Pydantic** - 数据验证

### 前端技术栈
- **原生HTML/CSS/JavaScript** - 无框架依赖
- **响应式设计** - CSS Grid + Flexbox
- **现代UI设计** - 毛玻璃效果、渐变背景
- **实时通信** - Fetch API

### AI技术栈
- **OpenAI GPT-4** - 大语言模型
- **BGE Embedding** - 中文文本向量化
- **PyMuPDF** - PDF文档解析
- **Sentence Transformers** - 文本相似度计算

## 📋 使用指南

### 1. 用户注册/登录
- 打开前端页面
- 输入手机号快速登录
- 系统自动创建用户账户

### 2. 选择专业领域
- 在左侧面板选择感兴趣的专业领域
- 每个领域都有专门的AI助手
- 可以随时切换不同领域

### 3. 开始提问
- 在输入框中输入问题
- 支持自然语言提问
- 系统会基于选择的专业领域提供精准回答

### 4. 查看历史
- 系统自动保存查询历史
- 可以查看个人学习记录
- 支持历史问题重新提问

## 🧪 测试验证

```bash
# 运行系统测试脚本
python3 scripts/test_system.py
```

测试包括：
- API健康检查
- 用户注册/登录
- Agent列表获取
- 智能问答功能
- 用户资料管理

## 📊 系统功能

### 用户管理
- ✅ 手机号快速登录
- ✅ JWT Token认证
- ✅ 用户资料管理
- ✅ 查询历史记录
- ✅ 学习统计信息

### 智能问答
- ✅ 多Agent协作处理
- ✅ 专业领域识别
- ✅ 精确版本控制
- ✅ 来源追溯标注
- ✅ 置信度评估

### 界面体验
- ✅ 响应式设计
- ✅ 实时聊天界面
- ✅ 专业领域切换
- ✅ 移动端适配
- ✅ 现代化UI设计

## 🔧 配置说明

### 环境变量配置

```bash
# LLM配置
LLM_PROVIDER=openai
OPENAI_API_KEY=your-api-key
LLM_MODEL=gpt-4-turbo-preview

# 认证配置
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=43200

# 数据库配置
DATABASE_URL=sqlite:///./dt_study_companion.db

# 向量数据库配置
VECTOR_DB=chroma
CHROMA_PATH=./database/chroma_db
```

### 书籍元数据配置

编辑 `data/books_metadata.json` 文件，添加您的教材信息：

```json
{
  "books": [
    {
      "id": "epidemiology",
      "name": "流行病学",
      "versions": [
        {
          "version": "7",
          "filename": "流行病学_第7版.pdf",
          "isbn": "978-7-117-15677-5",
          "publisher": "人民卫生出版社",
          "publish_year": 2012,
          "authors": ["李立明"],
          "pages": 350
        }
      ]
    }
  ]
}
```

## 🚨 常见问题

### 1. 启动失败
- 检查Python版本（需要3.8+）
- 确认所有依赖已安装
- 检查.env文件配置

### 2. API连接失败
- 确认服务器已启动
- 检查端口8000是否被占用
- 验证API密钥配置

### 3. 前端无法访问
- 直接打开HTML文件
- 检查浏览器控制台错误
- 确认API服务正常运行

## 🔮 扩展方向

### 功能扩展
- 添加更多专业领域
- 支持更多教材格式
- 增加学习进度跟踪
- 添加用户学习报告

### 技术优化
- 集成更多LLM提供商
- 优化向量检索算法
- 添加缓存机制
- 支持分布式部署

## 📞 技术支持

如果在使用过程中遇到问题：

1. 查看API文档：http://localhost:8000/docs
2. 检查日志文件：`logs/` 目录
3. 运行测试脚本：`python3 scripts/test_system.py`
4. 查看环境配置：`.env` 文件

## 📄 许可证

本项目采用 MIT 许可证。

## 👥 贡献

欢迎提交Issue和Pull Request来改进项目！

---

**DT-Study-Companion** - 为你的公共卫生学专业学习之路提供温度与智慧的陪伴！🎓✨