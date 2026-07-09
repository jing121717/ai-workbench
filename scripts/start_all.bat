@echo off
REM AI Workbench Windows 一键启动脚本
echo ==========================================
echo   AI Workbench 一键启动脚本
echo ==========================================

REM 启动 Docker Compose（后台）
echo [1/3] 启动 Docker 服务（MySQL + Redis）...
docker compose up -d db redis

REM 安装后端依赖
echo [2/3] 安装后端依赖...
python -m venv .venv
call .venv\Scripts\activate
pip install -r requirements.txt
python backend\init_db.py

REM 启动后端
echo [3/3] 启动后端服务...
start "AI Workbench Backend" cmd /k "call .venv\Scripts\activate && uvicorn backend.app.main:app --host 0.0.0.0 --port 8000"

REM 启动前端
cd frontend
call npm install
call npm run dev -- --host 0.0.0.0

echo ==========================================
echo   服务已启动！
echo   后端 API：http://localhost:8000
echo   前端页面：http://localhost:5173
echo   默认账号：admin / Admin@123456
echo ==========================================
pause
