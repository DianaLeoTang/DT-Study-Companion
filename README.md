<!--
 * @Author: Diana Tang
-->
# DT-Study-Companion
清瑶书院AI助教，为你的公共卫生研学之路提供温度与智慧的陪伴。

# 多Agent课本助手完整项目

## 📁 项目结构

```
textbook-assistant/
├── data/                          # 存放PDF文件
│   ├── raw_pdfs/                 # 原始PDF
│   │   ├── 流行病学_第7版.pdf
│   │   ├── 流行病学_第8版.pdf
│   │   └── ...
│   ├── processed/                # 处理后的数据
│   └── books_metadata.json       # 书籍元数据
├── database/                      # 向量数据库存储
│   └── chroma_db/
├── src/                          # 源代码
│   ├── __init__.py
│   ├── agents/                   # Agent模块
│   │   ├── __init__.py
│   │   ├── query_parser.py
│   │   ├── version_validator.py
│   │   ├── retriever.py
│   │   └── answer_generator.py
│   ├── preprocessing/            # 数据预处理
│   │   ├── __init__.py
│   │   ├── pdf_parser.py
│   │   └── vectorstore_builder.py
│   ├── workflow/                 # LangGraph工作流
│   │   ├── __init__.py
│   │   └── agent_graph.py
│   └── utils/                    # 工具函数
│       ├── __init__.py
│       ├── config.py
│       └── llm_client.py
├── api/                          # FastAPI接口
│   ├── __init__.py
│   ├── main.py
│   └── schemas.py
├── tests/                        # 测试
│   ├── test_agents.py
│   └── test_api.py
├── scripts/                      # 脚本
│   ├── setup_database.py        # 初始化数据库
│   └── process_books.py         # 批量处理PDF
├── requirements.txt              # 依赖
├── .env.example                  # 环境变量示例
├── docker-compose.yml            # Docker配置
├── Dockerfile
└── README.md                     # 说明文档
```

## 🚀 快速开始 (2天计划)

### Day 1: 环境搭建 + 数据处理

**上午 (2-3小时):**
1. 环境安装
2. 配置API密钥
3. 准备书籍元数据

**下午 (3-4小时):**
1. 运行PDF处理脚本
2. 构建向量数据库
3. 测试检索功能

### Day 2: Agent开发 + API部署

**上午 (3-4小时):**
1. 测试Multi-Agent工作流
2. 调试版本验证逻辑

**下午 (2-3小时):**
1. 启动FastAPI服务
2. 测试完整流程
3. 部署到服务器

## 📦 依赖清单

详见 requirements.txt
