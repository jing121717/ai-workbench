@echo off
chcp 65001 >nul
echo ═══════════════════════════════════════════
echo   AI Workbench · PyInstaller EXE 打包
echo ═══════════════════════════════════════════

cd /d "%~dp0\.."

if not exist "gui\venv\Scripts\activate.bat" (
    echo [ERROR] 未找到虚拟环境，请先运行 setup_gui_env.bat
    pause
    exit /b 1
)

call gui\venv\Scripts\activate.bat

echo [1/3] 安装 PyInstaller...
pip install pyinstaller -q

echo [2/3] 清理旧构建...
if exist "gui\dist" rmdir /s /q "gui\dist"
if exist "gui\build" rmdir /s /q "gui\build"

echo [3/3] 开始打包 AIWorkbench.exe...
pyinstaller gui\ai_workbench.spec --noconfirm

if exist "gui\dist\AIWorkbench" (
    echo.
    echo ═══════════════════════════════════════════
    echo   打包成功！
    echo   EXE 目录: gui\dist\AIWorkbench\AIWorkbench.exe
    echo ═══════════════════════════════════════════
    echo.
    echo 运行 EXE:
    echo   gui\dist\AIWorkbench\AIWorkbench.exe
    echo.
    echo 双击即可运行，无需 Python 环境。
    echo.
) else (
    echo [ERROR] 打包失败，请检查错误信息
)

pause
