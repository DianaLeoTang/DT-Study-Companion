# 📦 详细安装指南

## 系统要求

### 硬件要求
- **CPU**: 4核及以上（推荐8核）
- **内存**: 最低8GB（推荐16GB+）
- **硬盘**: 至少20GB可用空间
- **GPU**: 可选，用于加速Embedding（NVIDIA显卡，CUDA 11.8+）

### 软件要求
- **操作系统**: Linux / macOS / Windows 10+
- **Python**: 3.8 - 3.11（推荐3.10）
- **pip**: 20.0+

## 快速安装（推荐）

### Linux / macOS

```bash
# 1. 克隆或创建项目目录
mkdir textbook-assistant && cd textbook-assistant

# 2. 运行快速启动脚本
chmod +x scripts/quick_start.sh
./scripts/quick_start.sh
```

### Windows

```powershell
# 1. 创建项目目录
mkdir textbook-assistant
cd textbook-assistant

# 2. 创建虚拟环境
python -m venv venv
.\venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
copy .env.example .env
notepad .env

# 5. 处理PDF
python scripts\process_books.py

# 6. 启动服务
python api\main.py
```

## 详细安装步骤

### 1. Python环境准备

#### 安装Python 3.10（推荐版本）

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3.10 python3.10-venv python3.10-dev
```

**CentOS/RHEL:**
```bash
sudo yum install python310 python310-devel
```

**macOS (使用Homebrew):**
```bash
brew install python@3.10
```

**Windows:**
从 [Python官网](https://www.python.org/downloads/) 下载安装包

#### 验证安装
```bash
python3 --version  # 应显示 Python 3.10.x
```

### 2. 创建虚拟环境

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
# Linux/macOS:
source venv/bin/activate

# Windows:
venv\Scripts\activate

# 验证
which python  # Linux/macOS
where python  # Windows
```

### 3. 安装依赖包

#### 基础依赖
```bash
# 升级pip
pip install --upgrade pip setuptools wheel

# 安装项目依赖
pip install -r requirements.txt
```

#### GPU支持（可选）
如果有NVIDIA GPU，安装CUDA版本的PyTorch：

```bash
# CUDA 11.8
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# CUDA 12.1
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

验证GPU：
```python
python -c "import torch; print(f'GPU可用: {torch.cuda.is_available()}')"
```

### 4. 配置环境变量

#### 复制配置模板
```bash
cp .env.example .env
```

#### 编辑配置文件
```bash
nano .env  # 或使用你喜欢的编辑器
```

#### 必需配置项

**选择LLM提供商（三选一）：**

1. **OpenAI** (推荐)
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-xxxxx
OPENAI_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4-turbo-preview
```

2. **Anthropic Claude**
```bash
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-xxxxx
LLM_MODEL=claude-3-sonnet-20240229
```

3. **阿里通义千问** (国内)
```bash
LLM_PROVIDER=dashscope
DASHSCOPE_API_KEY=sk-xxxxx
LLM_MODEL=qwen-max
```

#### 可选配置项

```bash
# Embedding模型（默认即可）
EMBEDDING_MODEL=BAAI/bge-large-zh-v1.5
EMBEDDING_DEVICE=cuda  # 或 cpu

# PDF处理
PDF_CHUNK_SIZE=800
PDF_CHUNK_OVERLAP=200

# 检索配置
RETRIEVAL_TOP_K=5
RETRIEVAL_SCORE_THRESHOLD=0.5

# API配置
API_PORT=8000
API_WORKERS=4
```

### 5. 准备数据文件

#### 创建目录结构
```bash
mkdir -p data/raw_pdfs
mkdir -p data/processed
mkdir -p database/chroma_db
mkdir -p logs
```

#### 配置书籍元数据
编辑 `data/books_metadata.json`：

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

#### 添加PDF文件
将PDF文件放入 `data/raw_pdfs/` 目录，确保文件名与元数据中的 `filename` 字段完全一致。

#### 验证文件
```bash
python scripts/process_books.py --check-only
```

### 6. 处理PDF并构建数据库

#### 首次处理
```bash
python scripts/process_books.py
```

处理时间估算：
- 1本书（350页）：约 2-3 分钟
- 9本书：约 20-30 分钟

#### 重新构建
```bash
python scripts/process_books.py --force
```

#### 查看处理日志
```bash
tail -f logs/app_$(date +%Y-%m-%d).log
```

### 7. 测试系统

#### 运行测试脚本
```bash
python scripts/test_system.py
```

#### 手动测试
```python
from src.workflow.agent_graph import TextbookAssistant

assistant = TextbookAssistant()
result = assistant.query("流行病学第7版，什么是队列研究？")
print(result['answer'])
```

### 8. 启动服务

#### 开发模式
```bash
# 方式1: 直接运行
python api/main.py

# 方式2: 使用uvicorn（支持热重载）
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 生产模式
```bash
# 使用多个worker
uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4

# 或使用gunicorn + uvicorn
gunicorn api.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

#### 验证服务
```bash
# 健康检查
curl http://localhost:8000/health

# API文档
浏览器打开: http://localhost:8000/docs
```

## 常见问题排查

### 1. Python版本不兼容

**症状**: `SyntaxError` 或 `ImportError`

**解决**:
```bash
# 检查Python版本
python --version

# 如果版本不对，使用正确的Python
python3.10 -m venv venv
```

### 2. 依赖安装失败

**症状**: `pip install` 报错

**解决**:
```bash
# 更新pip
pip install --upgrade pip

# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 分步安装
pip install langchain langchain-community
pip install chromadb sentence-transformers
pip install fastapi uvicorn
```

### 3. Embedding模型下载慢

**症状**: 卡在 "Downloading model..."

**解决**:
```bash
# 使用国内镜像
export HF_ENDPOINT=https://hf-mirror.com
python scripts/process_books.py

# 或手动下载模型
mkdir -p ~/.cache/huggingface/hub
# 从 https://hf-mirror.com 下载模型文件
```

### 4. 内存不足

**症状**: `MemoryError` 或系统卡死

**解决**:
```bash
# 减小chunk大小
PDF_CHUNK_SIZE=500  # 在.env中

# 减小batch大小
EMBEDDING_BATCH_SIZE=8  # 在.env中

# 使用CPU而非GPU
EMBEDDING_DEVICE=cpu
```

### 5. PDF解析失败

**症状**: "PDF解析失败"

**解决**:
```bash
# 方案1: 安装额外依赖
pip install "unstructured[pdf]"

# 方案2: 使用OCR
pip install pytesseract pillow

# 方案3: 转换PDF格式
# 使用Adobe Acrobat或在线工具重新保存PDF
```

### 6. API连接失败

**症状**: `Connection refused`

**解决**:
```bash
# 检查服务是否运行
ps aux | grep uvicorn

# 检查端口占用
lsof -i :8000  # Linux/macOS
netstat -ano | findstr :8000  # Windows

# 检查防火墙
sudo ufw allow 8000  # Linux
```

### 7. LLM API调用失败

**症状**: "API调用失败"

**解决**:
```bash
# 检查API密钥
echo $OPENAI_API_KEY

# 测试API连接
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"

# 检查代理设置
export HTTP_PROXY=http://127.0.0.1:7890
export HTTPS_PROXY=http://127.0.0.1:7890
```

## 性能优化建议

### 1. 使用GPU加速
```bash
# 安装CUDA版本PyTorch
pip install torch --index-url https://download.pytorch.org/whl/cu118

# 在.env中启用GPU
EMBEDDING_DEVICE=cuda
```

### 2. 启用Redis缓存
```bash
# 启动Redis
docker run -d -p 6379:6379 redis:7-alpine

# 在.env中启用
REDIS_ENABLED=true
```

### 3. 使用Qdrant替代Chroma
```bash
# 启动Qdrant
docker run -p 6333:6333 qdrant/qdrant

# 在.env中配置
VECTOR_DB=qdrant
QDRANT_HOST=localhost
QDRANT_PORT=6333
```

### 4. 调优参数
```bash
# 增加检索数量
RETRIEVAL_TOP_K=10

# 降低相似度阈值
RETRIEVAL_SCORE_THRESHOLD=0.3

# 增加chunk重叠
PDF_CHUNK_OVERLAP=300
```

## 下一步

安装完成后，请参考：
- [README.md](README.md) - 使用文档
- [API文档](http://localhost:8000/docs) - API接口说明
- [frontend/index.html](frontend/index.html) - Web界面

开始使用：
```bash
# 启动API
python api/main.py

# 打开Web界面
open frontend/index.html  # macOS
xdg-open frontend/index.html  # Linux
start frontend/index.html  # Windows
```

祝使用愉快！🎉