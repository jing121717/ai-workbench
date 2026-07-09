"""
AI Workbench · PySide6 桌面客户端主窗口
三栏布局：会话列表 | 对话区 | 知识库/设置
"""
import sys
from pathlib import Path
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QSplitter,
    QListWidget, QTextBrowser, QTextEdit, QPushButton, QLabel,
    QLineEdit, QTabWidget, QFileDialog, QMessageBox, QApplication,
    QListWidgetItem, QComboBox, QPlainTextEdit, QInputDialog,
)
from PySide6.QtGui import QFont, QPalette, QColor
from gui.app.api_client import ApiClient
from gui.app.cache import LocalCache
from gui.app.workers import ChatWorker, UploadWorker
from gui.app.offline_service import OfflineService
from gui.app.file_watcher import ProjectFileWatcher


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("AI Workbench · 全栈智能代码工作台")
        self.resize(1360, 860)
        self.setMinimumSize(960, 600)

        # 深色主题
        self._apply_dark_palette()

        # 核心组件
        self.cache = LocalCache()
        self.api = ApiClient(
            base_url=self.cache.get_setting("base_url", "http://127.0.0.1:8000")
        )
        self.api.token = self.cache.get_setting("token", "")
        self.current_session_id: int | None = None
        self.current_project_id: int | None = None
        self.current_watch_path: str = ""
        self._project_watcher: ProjectFileWatcher | None = None
        self.offline = OfflineService()
        self._chat_workers: list[ChatWorker] = []

        self._build_ui()
        self._load_sessions()
        self._load_documents()
        self._load_code_projects()
        self._load_snippets()

        # 定时器：清理已完成的 worker
        QTimer.singleShot(3000, self._cleanup_workers)

    def _apply_dark_palette(self) -> None:
        dark = """
            QWidget { background-color: #0d1117; color: #e6edf3; font-family: Inter, sans-serif; }
            QMainWindow { background-color: #0d1117; }
            QLabel { color: #e6edf3; }
            QPushButton { background-color: #21262d; color: #e6edf3; border: 1px solid #30363d;
                          border-radius: 6px; padding: 6px 16px; }
            QPushButton:hover { border-color: #58a6ff; color: #58a6ff; }
            QPushButton:pressed { background-color: #30363d; }
            QTextBrowser { background-color: #161b22; color: #e6edf3; border: 1px solid #30363d;
                           border-radius: 8px; padding: 8px; }
            QTextEdit { background-color: #161b22; color: #e6edf3; border: 1px solid #30363d;
                        border-radius: 8px; padding: 8px; }
            QLineEdit { background-color: #161b22; color: #e6edf3; border: 1px solid #30363d;
                        border-radius: 6px; padding: 6px 12px; }
            QListWidget { background-color: #161b22; color: #e6edf3; border: none; }
            QListWidget::item { padding: 8px; border-radius: 4px; margin: 2px 0; }
            QListWidget::item:selected { background-color: rgba(88,166,255,.15); border-left: 2px solid #58a6ff; }
            QListWidget::item:hover { background-color: #21262d; }
            QTabWidget::pane { border: 1px solid #30363d; border-radius: 8px; background: #161b22; }
            QTabBar::tab { background: #161b22; color: #8b949e; padding: 8px 20px; border-top-left-radius: 6px; border-top-right-radius: 6px; }
            QTabBar::tab:selected { background: #21262d; color: #58a6ff; border-bottom: 2px solid #58a6ff; }
            QScrollBar:vertical { background: #0d1117; width: 6px; }
            QScrollBar::handle:vertical { background: #30363d; border-radius: 3px; }
        """
        self.setStyleSheet(dark)

    # ── UI 构建 ────────────────────────────────────────────────────────────────
    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)

        splitter = QSplitter(Qt.Orientation.Horizontal, central)
        splitter.setSizes([220, 700, 380])
        splitter.setStretchFactor(1, 3)
        splitter.setStretchFactor(2, 2)

        # ── 左侧：会话列表 ────────────────────────────────────────────────────
        left = self._build_sidebar()
        splitter.addWidget(left)

        # ── 中间：对话区 ──────────────────────────────────────────────────────
        center = self._build_chat_area()
        splitter.addWidget(center)

        # ── 右侧：知识库 / 设置 ──────────────────────────────────────────────
        right = self._build_knowledge_panel()
        splitter.addWidget(right)

        layout.addWidget(splitter)

    def _build_sidebar(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(8, 8, 8, 8)

        # Logo
        logo = QLabel("🤖 AI Workbench")
        logo.setStyleSheet("font-size: 1rem; font-weight: 700; padding: 8px; color: #58a6ff;")
        layout.addWidget(logo)

        new_btn = QPushButton("➕ 新建会话")
        new_btn.clicked.connect(self._new_session)
        layout.addWidget(new_btn)

        self.session_list = QListWidget()
        self.session_list.itemClicked.connect(self._select_session)
        layout.addWidget(self.session_list)

        layout.addStretch()

        # 底部状态
        self.status_label = QLabel("● 离线模式")
        self.status_label.setStyleSheet("color: #6e7681; font-size: .7rem; padding: 4px;")
        layout.addWidget(self.status_label)

        return w

    def _build_chat_area(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(12, 12, 12, 12)

        self.chat_display = QTextBrowser()
        self.chat_display.setOpenExternalLinks(True)
        layout.addWidget(self.chat_display)

        input_row = QWidget()
        input_layout = QHBoxLayout(input_row)
        input_layout.setContentsMargins(0, 0, 0, 0)

        self.input_edit = QTextEdit()
        self.input_edit.setPlaceholderText("输入消息，Enter 发送，Shift+Enter 换行...")
        self.input_edit.setMaximumHeight(100)
        self.input_edit.keyPressEvent = self._input_keyPress

        send_btn = QPushButton("▶ 发送")
        send_btn.setStyleSheet("background: linear-gradient(135deg, #58a6ff, #39d0d8); color: #fff; border: none; font-weight: 700;")
        send_btn.clicked.connect(self._send_message)

        input_layout.addWidget(self.input_edit, 1)
        input_layout.addWidget(send_btn, 0)

        layout.addWidget(input_row)
        return w

    def _build_knowledge_panel(self) -> QWidget:
        tabs = QTabWidget()

        # ── 知识库 ──────────────────────────────────────────────────────────
        kb_tab = QWidget()
        kb_layout = QVBoxLayout(kb_tab)

        upload_btn = QPushButton("📤 上传 PDF/TXT 文档")
        upload_btn.clicked.connect(self._upload_document)
        kb_layout.addWidget(upload_btn)

        self.doc_list = QListWidget()
        self.doc_list.itemDoubleClicked.connect(self._doc_double_clicked)
        kb_layout.addWidget(self.doc_list)

        kb_layout.addStretch()

        code_tab = self._build_code_project_tab()
        tools_tab = self._build_code_tools_tab()
        snippets_tab = self._build_snippets_tab()

        # ── 设置 ─────────────────────────────────────────────────────────────
        settings_tab = QWidget()
        settings_layout = QVBoxLayout(settings_tab)

        settings_layout.addWidget(QLabel("⚙️ 服务配置"))
        settings_layout.addSpacing(8)

        url_label = QLabel("后端 API 地址：")
        settings_layout.addWidget(url_label)
        self.url_input = QLineEdit(self.cache.get_setting("base_url", "http://127.0.0.1:8000"))
        settings_layout.addWidget(self.url_input)

        user_label = QLabel("用户名：")
        settings_layout.addWidget(user_label)
        self.user_input = QLineEdit(self.cache.get_setting("username", "admin"))
        settings_layout.addWidget(self.user_input)

        pwd_label = QLabel("密码：")
        settings_layout.addWidget(pwd_label)
        self.pwd_input = QLineEdit(self.cache.get_setting("password", "Admin@123456"))
        self.pwd_input.setEchoMode(QLineEdit.EchoMode.Password)
        settings_layout.addWidget(self.pwd_input)

        offline_label = QLabel("离线模式（输入 true 启用）：")
        settings_layout.addWidget(offline_label)
        self.offline_input = QLineEdit(self.cache.get_setting("offline_mode", "false"))
        settings_layout.addWidget(self.offline_input)

        save_btn = QPushButton("💾 保存配置并登录")
        save_btn.clicked.connect(self._save_settings)
        settings_layout.addWidget(save_btn)

        health_btn = QPushButton("🔍 检测服务状态")
        health_btn.clicked.connect(self._check_health)
        settings_layout.addWidget(health_btn)

        settings_layout.addStretch()

        tabs.addTab(kb_tab, "📚 知识库")
        tabs.addTab(code_tab, "💻 代码项目")
        tabs.addTab(tools_tab, "🧠 代码工具")
        tabs.addTab(snippets_tab, "🧩 素材库")
        tabs.addTab(settings_tab, "⚙️ 设置")
        return tabs

    def _build_code_project_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)

        top_row = QWidget()
        top_layout = QHBoxLayout(top_row)
        top_layout.setContentsMargins(0, 0, 0, 0)

        refresh_btn = QPushButton("🔄 刷新项目")
        refresh_btn.clicked.connect(self._load_code_projects)
        watch_btn = QPushButton("👁 监听目录")
        watch_btn.clicked.connect(self._toggle_project_watcher)
        sync_btn = QPushButton("☁ 同步当前项目")
        sync_btn.clicked.connect(self._sync_current_project)

        top_layout.addWidget(refresh_btn)
        top_layout.addWidget(watch_btn)
        top_layout.addWidget(sync_btn)
        layout.addWidget(top_row)

        self.project_list = QListWidget()
        self.project_list.itemClicked.connect(self._select_code_project)
        layout.addWidget(self.project_list)

        search_row = QWidget()
        search_layout = QHBoxLayout(search_row)
        search_layout.setContentsMargins(0, 0, 0, 0)
        self.code_search_input = QLineEdit()
        self.code_search_input.setPlaceholderText("搜索函数名、类名、接口路径...")
        search_btn = QPushButton("🔍 检索")
        search_btn.clicked.connect(self._search_code)
        search_layout.addWidget(self.code_search_input, 1)
        search_layout.addWidget(search_btn)
        layout.addWidget(search_row)

        self.code_result_list = QListWidget()
        self.code_result_list.itemDoubleClicked.connect(self._show_code_result_detail)
        layout.addWidget(self.code_result_list)
        return w

    def _build_code_tools_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)

        tool_row = QWidget()
        tool_layout = QHBoxLayout(tool_row)
        tool_layout.setContentsMargins(0, 0, 0, 0)

        self.code_tool_combo = QComboBox()
        self.code_tool_combo.addItem("缺陷扫描", "defect")
        self.code_tool_combo.addItem("代码重构", "refactor")
        self.code_tool_combo.addItem("生成单测", "unit_test")

        self.code_lang_combo = QComboBox()
        for lang in ["python", "javascript", "typescript", "java", "go", "sql", "vue"]:
            self.code_lang_combo.addItem(lang, lang)

        run_btn = QPushButton("▶ 运行")
        run_btn.clicked.connect(self._run_code_tool)
        save_snippet_btn = QPushButton("💾 存为片段")
        save_snippet_btn.clicked.connect(self._save_tool_result_as_snippet)

        tool_layout.addWidget(self.code_tool_combo)
        tool_layout.addWidget(self.code_lang_combo)
        tool_layout.addWidget(run_btn)
        tool_layout.addWidget(save_snippet_btn)
        layout.addWidget(tool_row)

        self.code_input_edit = QPlainTextEdit()
        self.code_input_edit.setPlaceholderText("粘贴代码或日志内容...")
        self.code_input_edit.setMaximumBlockCount(5000)
        layout.addWidget(self.code_input_edit, 1)

        self.code_output_browser = QTextBrowser()
        layout.addWidget(self.code_output_browser, 1)
        return w

    def _build_snippets_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)

        top_row = QWidget()
        top_layout = QHBoxLayout(top_row)
        top_layout.setContentsMargins(0, 0, 0, 0)
        refresh_btn = QPushButton("🔄 刷新片段")
        refresh_btn.clicked.connect(self._load_snippets)
        save_input_btn = QPushButton("➕ 保存输入框为片段")
        save_input_btn.clicked.connect(self._save_chat_input_as_snippet)
        top_layout.addWidget(refresh_btn)
        top_layout.addWidget(save_input_btn)
        layout.addWidget(top_row)

        self.snippet_list = QListWidget()
        self.snippet_list.itemClicked.connect(self._select_snippet)
        layout.addWidget(self.snippet_list)

        self.snippet_preview = QTextBrowser()
        layout.addWidget(self.snippet_preview)

        use_btn = QPushButton("↩ 插入到对话输入框")
        use_btn.clicked.connect(self._insert_selected_snippet)
        layout.addWidget(use_btn)
        return w

    # ── 会话管理 ────────────────────────────────────────────────────────────────
    def _load_sessions(self) -> None:
        self.session_list.clear()
        for s in self.cache.get_sessions():
            self.session_list.addItem(f"{s['title'][:20]}")

    def _new_session(self) -> None:
        title = f"会话 {len(self.cache.get_sessions()) + 1}"
        session_id = len(self.cache.get_sessions()) + 1
        import datetime
        self.cache.save_session(session_id, title, datetime.datetime.now().isoformat(), datetime.datetime.now().isoformat())
        self.current_session_id = session_id
        self._load_sessions()
        self._clear_chat()
        self._append_system_message(f"✅ 新会话已创建：{title}")

    def _select_session(self, item) -> None:
        sessions = self.cache.get_sessions()
        title = item.text()
        for s in sessions:
            if s["title"][:20] == title:
                self.current_session_id = s["id"]
                self._load_messages(s["id"])
                break

    def _load_messages(self, session_id: int) -> None:
        self._clear_chat()
        for msg in self.cache.get_messages(session_id):
            role = msg["role"]
            content = msg["content"]
            if role == "user":
                self._append_user_message(content)
            else:
                self._append_ai_message(content)

    # ── 发送消息 ────────────────────────────────────────────────────────────────
    def _send_message(self) -> None:
        text = self.input_edit.toPlainText().strip()
        if not text:
            return
        self.input_edit.clear()

        if not self.current_session_id:
            self._new_session()

        self._append_user_message(text)
        self._append_ai_message("⏳ 思考中...")

        offline_enabled = self.offline_input.text().strip().lower() == "true"

        if offline_enabled or not self.api.health_check():
            # 离线模式
            answer = self.offline.answer(text)
            self._replace_last_ai_message(answer)
            self.cache.save_message(self.current_session_id, "assistant", answer)
            return

        worker = ChatWorker(self.api, self.cache, self.current_session_id, text)
        worker.token_delta.connect(self._replace_last_ai_message)
        worker.finished.connect(lambda: self._update_session_list())
        worker.error.connect(lambda e: self._replace_last_ai_message(f"❌ 错误：{e}"))
        worker.start()
        self._chat_workers.append(worker)

    def _input_keyPress(self, event) -> None:
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter) and not (event.modifiers() & Qt.KeyboardModifier.ShiftModifier):
            self._send_message()
        else:
            QTextEdit.keyPressEvent(self.input_edit, event)

    # ── 消息渲染 ───────────────────────────────────────────────────────────────
    def _clear_chat(self) -> None:
        self.chat_display.setHtml("")

    def _append_user_message(self, text: str) -> None:
        html = f"""
        <div style="display:flex; justify-content:flex-end; margin:8px 0;">
            <div style="max-width:72%; background:linear-gradient(135deg,#58a6ff,#3b82f6);
                        color:#fff; padding:10px 14px; border-radius:12px 12px 4px 12px; font-size:.88rem; line-height:1.6;">
                {text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br>')}
            </div>
        </div>
        """
        self.chat_display.append(html)
        self._scroll_to_bottom()

    def _append_ai_message(self, text: str) -> None:
        html = f"""
        <div style="display:flex; justify-content:flex-start; margin:8px 0;">
            <div style="max-width:72%; background:#21262d; border:1px solid #30363d;
                        color:#e6edf3; padding:10px 14px; border-radius:12px 12px 12px 4px; font-size:.88rem; line-height:1.6;">
                {text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br>')}
            </div>
        </div>
        """
        self.chat_display.append(html)
        self._scroll_to_bottom()

    def _append_system_message(self, text: str) -> None:
        html = f"""
        <div style="text-align:center; color:#6e7681; font-size:.75rem; margin:12px 0;">
            {text}
        </div>
        """
        self.chat_display.append(html)
        self._scroll_to_bottom()

    def _replace_last_ai_message(self, text: str) -> None:
        html = self.chat_display.toHtml()
        last_div_end = html.rfind("</div>")
        if last_div_end == -1:
            return
        prefix = html[:last_div_end]
        suffix = html[last_div_end + 6:]
        new_content = prefix.split("<div")[-1] if "<div" in prefix else ""
        new_html = prefix[:prefix.rfind("<div") if "<div" in prefix else 0] + f"""
        <div style="display:flex; justify-content:flex-start; margin:8px 0;">
            <div style="max-width:72%; background:#21262d; border:1px solid #30363d;
                        color:#e6edf3; padding:10px 14px; border-radius:12px 12px 12px 4px; font-size:.88rem; line-height:1.6;">
                {text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br>')}
            </div>
        </div>
        """ + suffix
        self.chat_display.setHtml(new_html)
        self._scroll_to_bottom()

    def _scroll_to_bottom(self) -> None:
        self.chat_display.verticalScrollBar().setValue(self.chat_display.verticalScrollBar().maximum())

    # ── 知识库 ────────────────────────────────────────────────────────────────
    def _load_documents(self) -> None:
        self.doc_list.clear()
        try:
            data = self.api.list_documents()
            docs = data.get("results", []) if isinstance(data, dict) else data
            for doc in docs:
                item = QListWidgetItem(f"{doc.get('title', '未命名文档')} ({doc.get('status', 'unknown')})")
                item.setData(Qt.ItemDataRole.UserRole, doc)
                self.doc_list.addItem(item)
        except Exception:
            pass

    def _upload_document(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "选择文档", str(Path.home()), "Documents (*.pdf *.txt)")
        if not path:
            return
        self.status_label.setText("● 上传中...")
        offline_enabled = self.offline_input.text().strip().lower() == "true"
        worker = UploadWorker(self.api, self.cache, offline_enabled, path)
        worker.succeeded.connect(lambda r: self._handle_upload_success(r, path))
        worker.failed.connect(lambda e: QMessageBox.critical(self, "失败", f"上传失败：{e}"))
        worker.start()

    def _doc_double_clicked(self, item) -> None:
        self._append_system_message("💡 提示：双击知识库文档后，将基于该文档进行提问。")

    def _handle_upload_success(self, result: dict, path: str) -> None:
        QMessageBox.information(self, "完成", f"文档处理成功：{result.get('title', Path(path).name)}")
        self._load_documents()

    # ── 代码项目 ──────────────────────────────────────────────────────────────
    def _load_code_projects(self) -> None:
        self.project_list.clear()
        projects: list[dict] = []
        try:
            data = self.api.list_code_projects()
            projects = list(data.get("owned", [])) + list(data.get("shared", []))
            self.cache.save_code_projects(projects)
        except Exception:
            projects = self.cache.get_code_projects()

        for project in projects:
            item = QListWidgetItem(f"{project.get('name', '未命名项目')} · {project.get('total_files', 0)} 文件")
            item.setData(Qt.ItemDataRole.UserRole, project)
            self.project_list.addItem(item)

    def _select_code_project(self, item) -> None:
        project = item.data(Qt.ItemDataRole.UserRole) or {}
        self.current_project_id = project.get("id")
        self.status_label.setText(f"● 当前项目：{project.get('name', '未命名项目')}")
        self._append_system_message(f"已切换到代码项目：{project.get('name', '未命名项目')}")

    def _sync_current_project(self) -> None:
        if not self.current_project_id:
            QMessageBox.information(self, "提示", "请先选择代码项目。")
            return
        try:
            result = self.api.sync_code_project(self.current_project_id)
            self._append_system_message(f"项目同步完成：{result.get('total_files', 0)} 文件 / {result.get('total_units', 0)} 单元")
            self._load_code_projects()
        except Exception as exc:
            QMessageBox.warning(self, "同步失败", str(exc))

    def _search_code(self) -> None:
        query = self.code_search_input.text().strip()
        if not query:
            return
        self.code_result_list.clear()
        try:
            data = self.api.search_code(query, self.current_project_id)
            for row in data.get("results", []):
                item = QListWidgetItem(f"{row.get('name', 'unknown')} · {Path(row.get('file_path', '')).name}:{row.get('line', 0)}")
                item.setData(Qt.ItemDataRole.UserRole, row)
                self.code_result_list.addItem(item)
        except Exception as exc:
            QMessageBox.warning(self, "检索失败", str(exc))

    def _show_code_result_detail(self, item) -> None:
        row = item.data(Qt.ItemDataRole.UserRole) or {}
        self.code_output_browser.setPlainText(row.get("content", ""))
        self._append_system_message(
            f"检索命中：{row.get('name', 'unknown')} · {row.get('file_path', '')}:{row.get('line', 0)}"
        )

    def _toggle_project_watcher(self) -> None:
        if self._project_watcher and self._project_watcher.is_running():
            self._project_watcher.stop()
            self.status_label.setText("● 文件监听已停止")
            return

        default_path = self.cache.get_setting("watch_project_path", str(Path.home()))
        selected_dir = QFileDialog.getExistingDirectory(self, "选择要监听的项目目录", default_path)
        if not selected_dir:
            return

        self.cache.set_setting("watch_project_path", selected_dir)
        self.current_watch_path = selected_dir
        self._project_watcher = ProjectFileWatcher(selected_dir, on_file_change=self._handle_project_file_change)
        if self._project_watcher.start():
            self.status_label.setText(f"● 监听中：{Path(selected_dir).name}")
            self._append_system_message(f"开始监听项目目录：{selected_dir}")
        else:
            QMessageBox.warning(self, "监听失败", "无法启动文件监听，请确认已安装 watchdog。")

    def _handle_project_file_change(self, event) -> None:
        try:
            if event.event_type == "deleted":
                return
            self.api.sync_file(
                file_path=event.file_path,
                content=event.content or "",
                language=event.language or "unknown",
                project_id=self.current_project_id,
            )
            self.status_label.setText(f"● 已同步：{Path(event.file_path).name}")
        except Exception:
            self.status_label.setText(f"● 本地变更：{Path(event.file_path).name}")

    # ── 代码工具 ──────────────────────────────────────────────────────────────
    def _run_code_tool(self) -> None:
        content = self.code_input_edit.toPlainText().strip()
        if not content:
            return
        tool = self.code_tool_combo.currentData()
        language = self.code_lang_combo.currentData()
        try:
            if tool == "defect":
                result = self.api.analyze_code(content, language, "defect")
            elif tool == "refactor":
                result = self.api.refactor_code(content, language, "readability")
            else:
                result = self.api.generate_unit_test(content, language, "pytest")
            import json
            self.code_output_browser.setPlainText(json.dumps(result, ensure_ascii=False, indent=2))
        except Exception as exc:
            self.code_output_browser.setPlainText(f"运行失败：{exc}")

    def _save_tool_result_as_snippet(self) -> None:
        content = self.code_output_browser.toPlainText().strip()
        if not content:
            QMessageBox.information(self, "提示", "当前没有可保存的结果。")
            return
        title, ok = QInputDialog.getText(self, "保存片段", "请输入片段标题：")
        if not ok or not title.strip():
            return
        try:
            self.api.create_snippet(title.strip(), content, self.code_lang_combo.currentData(), "tool_result")
            self._load_snippets()
            QMessageBox.information(self, "成功", "已保存到代码素材库。")
        except Exception as exc:
            QMessageBox.warning(self, "失败", str(exc))

    # ── 素材库 ────────────────────────────────────────────────────────────────
    def _load_snippets(self) -> None:
        self.snippet_list.clear()
        snippets: list[dict] = []
        try:
            data = self.api.list_snippets()
            snippets = data.get("list", [])
            self.cache.save_snippets(snippets)
        except Exception:
            snippets = self.cache.get_snippets()

        for snippet in snippets:
            item = QListWidgetItem(f"{snippet.get('title', '未命名片段')} · {snippet.get('language', '')}")
            item.setData(Qt.ItemDataRole.UserRole, snippet)
            self.snippet_list.addItem(item)

    def _select_snippet(self, item) -> None:
        snippet = item.data(Qt.ItemDataRole.UserRole) or {}
        snippet_id = snippet.get("id")
        try:
            detail = self.api.get_snippet(snippet_id)
        except Exception:
            detail = snippet
        item.setData(Qt.ItemDataRole.UserRole, detail)
        self.snippet_preview.setPlainText(detail.get("content", ""))

    def _insert_selected_snippet(self) -> None:
        current = self.snippet_list.currentItem()
        if not current:
            return
        snippet = current.data(Qt.ItemDataRole.UserRole) or {}
        content = snippet.get("content") or self.snippet_preview.toPlainText()
        self.input_edit.insertPlainText(content)

    def _save_chat_input_as_snippet(self) -> None:
        content = self.input_edit.toPlainText().strip()
        if not content:
            QMessageBox.information(self, "提示", "对话输入框没有内容。")
            return
        title, ok = QInputDialog.getText(self, "保存片段", "请输入片段标题：")
        if not ok or not title.strip():
            return
        try:
            self.api.create_snippet(title.strip(), content)
            self._load_snippets()
            QMessageBox.information(self, "成功", "片段已保存。")
        except Exception as exc:
            QMessageBox.warning(self, "失败", str(exc))

    # ── 设置 ──────────────────────────────────────────────────────────────────
    def _save_settings(self) -> None:
        self.cache.set_setting("base_url", self.url_input.text().strip())
        self.cache.set_setting("username", self.user_input.text().strip())
        self.cache.set_setting("password", self.pwd_input.text().strip())
        self.cache.set_setting("offline_mode", self.offline_input.text().strip().lower())

        self.api.base_url = self.url_input.text().strip()

        try:
            token = self.api.login(self.user_input.text().strip(), self.pwd_input.text().strip())
            self.cache.set_setting("token", token)
            self.status_label.setText("● 已连接")
            self.status_label.setStyleSheet("color: #3fb950; font-size: .7rem; padding: 4px;")
            self._load_documents()
            self._load_code_projects()
            self._load_snippets()
            QMessageBox.information(self, "成功", "登录成功，JWT 已保存！")
        except Exception as exc:
            QMessageBox.warning(self, "离线模式", f"无法连接在线服务，将继续支持离线模式。\n{exc}")
            self.status_label.setText("● 离线模式")
            self.status_label.setStyleSheet("color: #f0883e; font-size: .7rem; padding: 4px;")

    def _check_health(self) -> None:
        if self.api.health_check():
            QMessageBox.information(self, "服务状态", "✅ 后端服务运行正常！")
        else:
            QMessageBox.warning(self, "服务状态", "⚠️ 无法连接到后端服务，请检查服务是否启动。")

    def _update_session_list(self) -> None:
        QTimer.singleShot(500, self._load_sessions)

    def _cleanup_workers(self) -> None:
        self._chat_workers = [w for w in self._chat_workers if w.isRunning()]
        QTimer.singleShot(5000, self._cleanup_workers)

    def closeEvent(self, event) -> None:
        if self._project_watcher and self._project_watcher.is_running():
            self._project_watcher.stop()
        for w in self._chat_workers:
            w.quit()
            w.wait(1000)
        event.accept()
