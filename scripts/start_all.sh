#!/bin/bash
# 一键启动所有服务（适用于 macOS / Linux / Git Bash / WSL）
set -e

echo "=========================================="
echo "  AI Workbench 一键启动脚本"
echo "=========================================="

# 启动 Docker 服务（MySQL + Redis）
echo "[1/4] 检查 Docker 服务..."
if command -v docker &> /dev/null; then
    docker compose up -d db redis
    echo "  Docker 服务已启动 ✓"
else
    echo "  警告：未检测到 Docker，部分服务可能无法自动启动"
fi

# 安装后端依赖
echo "[2/4] 安装后端依赖..."
cd "$(dirname "$0")/.."
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python backend/init_db.py

# 启动后端
echo "[3/4] 启动后端服务..."
source .venv/bin/activate
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# 安装前端依赖并启动
echo "[4/4] 启动前端服务..."
cd frontend
npm install
npm run dev -- --host 0.0.0.0 &
FRONTEND_PID=$!

echo ""
echo "=========================================="
echo "  服务已启动！"
echo "  后端 API：http://localhost:8000"
echo "  前端页面：http://localhost:5173"
echo "  默认账号：admin / Admin@123456"
echo "=========================================="
echo ""
echo "按 Ctrl+C 可停止所有服务"

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait
