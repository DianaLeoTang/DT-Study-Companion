#!/bin/bash
# 查看后端服务状态

cd "$(dirname "$0")"

PID_FILE=".backend.pid"

echo "=== 后端服务状态 ==="

if [ ! -f "$PID_FILE" ]; then
    echo "状态: ❌ 未运行"
    exit 0
fi

PID=$(cat "$PID_FILE")

if ps -p $PID > /dev/null 2>&1; then
    echo "状态: ✅ 运行中"
    echo "PID: $PID"
    echo "地址: http://localhost:8000"
    echo ""
    echo "最近日志:"
    tail -n 10 backend.log 2>/dev/null || echo "无日志文件"
else
    echo "状态: ❌ 进程不存在 (PID文件存在但进程已结束)"
    rm "$PID_FILE"
fi

