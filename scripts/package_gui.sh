#!/bin/bash
# AI Workbench · PyInstaller 打包脚本（macOS / Linux / Git Bash）
set -e

echo "=========================================="
echo "  AI Workbench EXE 打包脚本"
echo "=========================================="

cd "$(dirname "$0")/.."

# 安装打包依赖
echo "[1/4] 安装 PyInstaller..."
pip install pyinstaller pyside6 requests

# 安装桌面端依赖
echo "[2/4] 安装桌面端依赖..."
pip install -r requirements.txt

# 打包
echo "[3/4] 执行 PyInstaller 打包..."
cd gui
pyinstaller ai_workbench.spec --clean

# 打包结果
echo "[4/4] 打包完成！"
DIST_PATH="$(dirname "$0")/../gui/dist/AIWorkbench"
if [ -d "$DIST_PATH" ]; then
    echo "=========================================="
    echo "  打包成功！"
    echo "  EXE 文件位置："
    echo "  $DIST_PATH/AIWorkbench（Linux/macOS）"
    echo "  $DIST_PATH/AIWorkbench.exe（Windows，通过 Wine 或 CrossOver）"
    echo "=========================================="
fi
