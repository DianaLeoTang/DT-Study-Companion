#!/bin/bash

# DT-Study-Companion 快速启动脚本

echo "🎓 DT-Study-Companion 快速启动"
echo "=================================="

# 检查Python版本
python_version=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ 错误: 需要Python 3.8或更高版本"
    echo "当前版本: $(python3 --version)"
    exit 1
fi

echo "✅ Python版本检查通过: $(python3 --version)"

# 创建虚拟环境（如果不存在）
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate

# 升级pip
echo "⬆️  升级pip..."
pip install --upgrade pip

# 安装依赖
echo "📚 安装依赖包..."
pip install -r requirement.txt

# 创建必要的目录
echo "📁 创建目录结构..."
mkdir -p data/raw_pdfs
mkdir -p data/processed
mkdir -p database/chroma_db
mkdir -p logs

# 检查环境变量文件
if [ ! -f ".env" ]; then
    if [ -f "env.example" ]; then
        echo "⚙️  创建环境变量文件..."
        cp env.example .env
        echo "⚠️  请编辑 .env 文件，配置API密钥等参数"
    else
        echo "❌ 未找到环境变量配置文件"
        exit 1
    fi
fi

# 检查书籍元数据
if [ ! -f "data/books_metadata.json" ]; then
    echo "❌ 未找到书籍元数据文件: data/books_metadata.json"
    exit 1
fi

echo "✅ 环境准备完成！"
echo ""
echo "🚀 启动服务器..."
echo "   地址: http://localhost:8000"
echo "   API文档: http://localhost:8000/docs"
echo "   前端界面: file://$(pwd)/frontend/index.html"
echo ""
echo "按 Ctrl+C 停止服务器"
echo ""

# 启动服务器
python3 scripts/start_server.py
