#!/bin/bash
# 启动后端服务

cd "$(dirname "$0")"

PID_FILE=".backend.pid"

# 检查是否已经运行
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p $PID > /dev/null 2>&1; then
        echo "❌ 后端服务已经在运行 (PID: $PID)"
        echo "💡 使用 ./stop.sh 停止服务"
        exit 1
    else
        rm "$PID_FILE"
    fi
fi

echo "🚀 启动后端服务..."

# 启动后端
nohup python3 simple_backend.py > backend.log 2>&1 &
echo $! > "$PID_FILE"

sleep 2

# 检查是否启动成功
if ps -p $(cat "$PID_FILE") > /dev/null 2>&1; then
    echo "✅ 后端服务启动成功 (PID: $(cat "$PID_FILE"))"
    echo "🌐 地址: http://localhost:8000"
    echo "📖 API文档: http://localhost:8000/docs"
    echo "📝 日志文件: backend.log"
    echo ""
    echo "💡 使用 ./stop.sh 停止服务"
    echo "💡 使用 tail -f backend.log 查看日志"
else
    echo "❌ 后端服务启动失败"
    echo "📝 查看日志: cat backend.log"
    rm "$PID_FILE"
    exit 1
fi

