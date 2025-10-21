#!/bin/bash
# 停止后端服务

cd "$(dirname "$0")"

PID_FILE=".backend.pid"

if [ ! -f "$PID_FILE" ]; then
    echo "❌ 后端服务未运行"
    exit 1
fi

PID=$(cat "$PID_FILE")

if ! ps -p $PID > /dev/null 2>&1; then
    echo "❌ 后端服务进程不存在 (PID: $PID)"
    rm "$PID_FILE"
    exit 1
fi

echo "🛑 停止后端服务 (PID: $PID)..."

# 优雅地停止进程
kill -TERM $PID

# 等待进程结束
for i in {1..10}; do
    if ! ps -p $PID > /dev/null 2>&1; then
        echo "✅ 后端服务已停止"
        rm "$PID_FILE"
        exit 0
    fi
    sleep 1
done

# 如果还没停止，强制终止
echo "⚠️  进程未响应，强制终止..."
kill -9 $PID
sleep 1

if ! ps -p $PID > /dev/null 2>&1; then
    echo "✅ 后端服务已强制停止"
    rm "$PID_FILE"
else
    echo "❌ 无法停止后端服务"
    exit 1
fi

