
# 项目结构整理完成

## 🎯 新的项目结构

### 后端 (backend/)
- `app/` - 应用核心代码
  - `api/` - API路由 (auth, documents, queries, health)
  - `core/` - 核心配置 (config.py)
  - `models/` - 数据模型
  - `services/` - 业务服务
  - `main.py` - 应用入口
- `rag/` - RAG核心模块
  - `agents/` - RAG代理
  - `preprocessing/` - 文档预处理
  - `vectorstore/` - 向量存储
  - `llm/` - 大语言模型

### 前端 (frontend/)
- `public/` - 静态资源
  - `index.html` - 现代化主页面

### 数据 (data/)
- `documents/` - 原始文档
- `processed/` - 处理后的数据
- `database/` - 数据库文件

## 🚀 启动新系统

```bash
# 启动新的现代化系统
python start_new_system.py
```

## 📚 文档

- `README_NEW.md` - 新系统说明文档
- `PROJECT_STRUCTURE.md` - 项目结构设计文档

## 🗂️ 归档文件

旧文件已移动到 `archive/` 目录：
- `old_scripts/` - 旧脚本文件
- `old_docs/` - 旧文档文件  
- `old_frontend/` - 旧前端文件
- `duplicate_files/` - 重复文件

## ✨ 改进点

1. **前后端分离**: 清晰的架构设计
2. **模块化**: 可维护的代码结构
3. **现代化**: 最新的技术栈
4. **文档完善**: 详细的说明文档
5. **专业结构**: 符合行业标准
