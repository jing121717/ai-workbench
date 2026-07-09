#!/usr/bin/env python
"""
AI Workbench · PySide6 桌面客户端入口
支持 Web 离线使用，无需配置 Python 环境
"""
import sys
from pathlib import Path

if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    bundle_dir = Path(sys._MEIPASS)
else:
    bundle_dir = Path(__file__).parent

sys.path.insert(0, str(bundle_dir.parent))

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont
from gui.app.main_window import MainWindow


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("AI Workbench")

    # 全局字体
    font = QFont("Inter", 9)
    font.setStyleHint(QFont.StyleHint.SansSerif)
    app.setFont(font)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
