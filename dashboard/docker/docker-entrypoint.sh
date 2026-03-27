#!/bin/bash

set -e

echo "========================================"
echo "FX Predict Docker 容器启动"
echo "========================================"
echo "时区: ${TZ:-Asia/Shanghai}"
echo "Dashboard 端口: ${PORT:-3000}"
echo "定时任务: 每小时执行 run_full_pipeline.sh"
echo "========================================"

# 创建日志目录
mkdir -p /app/logs

# 设置 cron 任务（每小时执行一次）
echo "配置 cron 定时任务..."
echo "0 * * * * cd /app && bash run_full_pipeline.sh >> /app/logs/pipeline.log 2>&1" > /tmp/crontab
crontab /tmp/crontab

# 启动 cron 守护进程
echo "启动 cron 守护进程..."
crond -f -l 2 >> /app/logs/cron.log 2>&1 &
CRON_PID=$!

# 等待 cron 启动
sleep 2

# 验证 cron 任务是否配置成功
echo "验证 cron 配置..."
crontab -l

echo ""
echo "========================================"
echo "启动 Dashboard 服务器..."
echo "========================================"

# 启动 Dashboard 服务器
cd /app/dashboard && npm start

# 如果 Dashboard 退出，也关闭 cron
echo "Dashboard 已停止，关闭 cron 守护进程..."
kill $CRON_PID 2>/dev/null || true