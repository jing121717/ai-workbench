@echo off
chcp 65001 >nul
echo ═══════════════════════════════════════════
echo   AI Workbench · 创建桌面客户端虚拟环境
echo ═══════════════════════════════════════════

cd /d "%~dp0\.."

if exist "gui\venv" (
    echo [INFO] 虚拟环境已存在，跳过创建
    goto :activate
)

echo [1/2] 创建 Python 虚拟环境...
python -m venv gui\venv

if errorlevel 1 (
    echo [ERROR] 创建虚拟环境失败，请确保已安装 Python 3.10+
    pause
    exit /b 1
)

:activate
echo [2/2] 安装依赖包...
call gui\venv\Scripts\activate.bat

pip install --upgrade pip -q
pip install PySide6 requests -q

echo.
echo ═══════════════════════════════════════════
echo   环境创建完成！
echo ═══════════════════════════════════════════
echo.
echo 下一步:
echo   1. 运行打包: scripts\package_gui.bat
echo   2. 或直接运行桌面客户端:
echo      gui\venv\Scripts\python gui\main.py
echo.

pause
