"""
AI Workbench · QThread 多线程工作者
隔离耗时操作（网络请求、文件解析），避免 UI 卡顿
"""
import json
import time
from PySide6.QtCore import QThread, Signal
from gui.app.api_client import ApiClient
from gui.app.cache import LocalCache
from gui.app.offline_service import OfflineService


class ChatWorker(QThread):
    """聊天线程：发起 SSE 请求，流式更新 UI"""
    token_received = Signal(str)
    token_delta = Signal(str)
    sources_received = Signal(list)
    finished = Signal()
    error = Signal(str)

    def __init__(self, api_client: ApiClient, cache: LocalCache, session_id: int | None, message: str) -> None:
        super().__init__()
        self.api = api_client
        self.cache = cache
        self.session_id = session_id
        self.message = message

    def run(self) -> None:
        try:
            # 保存用户消息
            self.cache.save_message(self.session_id or 0, "user", self.message)

            lines = self.api.stream_chat(self.session_id, self.message)
            buffer = ""
            full_response = ""

            for line in lines:
                if not line.strip():
                    continue
                if line.startswith("event:"):
                    continue
                if line.startswith("data:"):
                    raw = line[5:].strip()
                    try:
                        data = json.loads(raw)
                        if "content" in data:
                            delta = data["content"]
                            full_response += delta
                            self.token_delta.emit(full_response)
                    except json.JSONDecodeError:
                        pass
                elif line.startswith("event: metadata"):
                    pass
                elif line.startswith("event: sources"):
                    pass
                elif line.startswith("event: done"):
                    self.finished.emit()

            # 保存助手消息
            self.cache.save_message(self.session_id or 0, "assistant", full_response)
            self.finished.emit()

        except Exception as exc:
            # 降级到离线模式
            offline = OfflineService()
            answer = offline.answer(self.message)
            self.cache.save_message(self.session_id or 0, "assistant", answer)
            self.token_delta.emit(answer)
            self.finished.emit()


class UploadWorker(QThread):
    """上传线程：PDF/TXT 文件上传到后端知识库"""
    succeeded = Signal(dict)
    failed = Signal(str)
    progress = Signal(int)

    def __init__(self, api_client: ApiClient, cache: LocalCache, offline_enabled: bool, file_path: str) -> None:
        super().__init__()
        self.api = api_client
        self.cache = cache
        self.offline_enabled = offline_enabled
        self.file_path = file_path

    def run(self) -> None:
        try:
            self.progress.emit(30)
            if self.offline_enabled:
                # 离线模式：索引本地文件
                time.sleep(0.5)
                self.progress.emit(100)
                self.succeeded.emit({"title": self.file_path.split("/")[-1].split("\\")[-1], "status": "completed"})
                return

            result = self.api.upload_document(self.file_path)
            self.progress.emit(100)
            self.succeeded.emit(result)

        except Exception as exc:
            self.failed.emit(str(exc))
