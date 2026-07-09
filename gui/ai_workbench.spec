# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller 打包配置
双击即可运行，无需安装 Python 环境
"""
import sys
from pathlib import Path

block_cipher = None

SPEC_DIR = Path("D:/vscode/ai-workbench/gui")
BACKEND_DIR = Path("D:/vscode/ai-workbench/backend")

a = Analysis(
    [str(SPEC_DIR / "main.py")],
    pathex=[str(SPEC_DIR)],
    binaries=[],
    datas=[
        (str(BACKEND_DIR / "knowledge_base.py"), "backend"),
        (str(SPEC_DIR / "app"), "gui/app"),
    ],
    hiddenimports=[
        "requests",
        "sqlite3",
        "watchdog",
        "watchdog.events",
        "watchdog.observers",
        "PySide6",
        "PySide6.QtCore",
        "PySide6.QtGui",
        "PySide6.QtWidgets",
        "gui.app.api_client",
        "gui.app.cache",
        "gui.app.file_watcher",
        "gui.app.workers",
        "gui.app.offline_service",
        "gui.app.main_window",
    ],
    hookspath=[],
    hooksconfig={},
    keys=[],
    cryptograph_cert=None,
    cryptograph_key=None,
    curves=[],
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="AIWorkbench",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # 不显示控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="AIWorkbench",
)
