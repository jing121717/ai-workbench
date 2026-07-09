import os
import time
import threading
from pathlib import Path
from typing import Callable, Dict, List, Optional, Set
from dataclasses import dataclass
import hashlib

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler, FileModifiedEvent, FileCreatedEvent, FileDeletedEvent
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False

SUPPORTED_EXTENSIONS = {
    '.py', '.js', '.ts', '.tsx', '.vue', '.java', '.go', '.rs',
    '.sql', '.sh', '.yaml', '.yml', '.json', '.xml', '.md',
    '.html', '.css', '.scss', '.less', '.jsx', '.kt', '.swift',
    '.cs', '.rb', '.php', '.c', '.cpp', '.h', '.hpp'
}

IGNORE_DIRS = {
    '.git', '__pycache__', 'node_modules', 'venv', '.venv',
    'env', '.env', 'dist', 'build', 'target', 'bin', 'obj',
    '.idea', '.vscode', 'vendor', 'packages', '.egg-info',
    'coverage', '.tox', '.pytest_cache', '.mypy_cache', '.venv_cache'
}

@dataclass
class FileChangeEvent:
    event_type: str
    file_path: str
    content: Optional[str] = None
    language: Optional[str] = None
    timestamp: float = 0

class ProjectFileHandler(FileSystemEventHandler):
    """项目文件事件处理器"""

    def __init__(self, watcher: 'ProjectFileWatcher'):
        self.watcher = watcher
        self.debounce_dict: Dict[str, float] = {}
        self.debounce_delay = 1.0

    def should_process(self, path: str) -> bool:
        if not path:
            return False

        path_obj = Path(path)

        if path_obj.is_dir():
            return False

        if any(ignored in path for ignored in IGNORE_DIRS):
            return False

        if path_obj.suffix.lower() not in SUPPORTED_EXTENSIONS:
            return False

        if path_obj.name.startswith('.'):
            return False

        return True

    def on_modified(self, event: FileModifiedEvent):
        if event.is_directory:
            return

        if not self.should_process(event.src_path):
            return

        self._debounce_and_notify('modified', event.src_path)

    def on_created(self, event: FileCreatedEvent):
        if event.is_directory:
            return

        if not self.should_process(event.src_path):
            return

        self._notify('created', event.src_path)

    def on_deleted(self, event: FileDeletedEvent):
        if event.is_directory:
            return

        if not self.should_process(event.src_path):
            return

        self._notify('deleted', event.src_path)

    def _debounce_and_notify(self, event_type: str, file_path: str):
        """防抖处理"""
        current_time = time.time()
        last_time = self.debounce_dict.get(file_path, 0)

        if current_time - last_time < self.debounce_delay:
            return

        self.debounce_dict[file_path] = current_time

        self._notify(event_type, file_path)

    def _notify(self, event_type: str, file_path: str):
        """通知文件变更"""
        try:
            content = None
            if event_type != 'deleted':
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                except Exception:
                    pass

            change_event = FileChangeEvent(
                event_type=event_type,
                file_path=file_path,
                content=content,
                language=self._detect_language(file_path),
                timestamp=time.time()
            )

            if self.watcher.on_file_change:
                self.watcher.on_file_change(change_event)

        except Exception as e:
            print(f"[FileWatcher] Error processing {event_type} for {file_path}: {e}")

    @staticmethod
    def _detect_language(file_path: str) -> str:
        """检测语言"""
        ext = Path(file_path).suffix.lower()
        lang_map = {
            '.py': 'python', '.js': 'javascript', '.ts': 'typescript',
            '.tsx': 'typescript', '.jsx': 'javascript', '.vue': 'vue',
            '.java': 'java', '.go': 'go', '.rs': 'rust', '.sql': 'sql',
            '.sh': 'bash', '.rb': 'ruby', '.php': 'php', '.c': 'c',
            '.cpp': 'cpp', '.h': 'c', '.hpp': 'cpp', '.cs': 'csharp',
            '.kt': 'kotlin', '.swift': 'swift', '.rb': 'ruby'
        }
        return lang_map.get(ext, 'unknown')

class ProjectFileWatcher:
    """项目文件监听器 - 监听项目目录文件变更"""

    def __init__(
        self,
        project_path: str,
        on_file_change: Callable[[FileChangeEvent], None] = None,
        on_error: Callable[[Exception], None] = None
    ):
        self.project_path = Path(project_path)
        self.on_file_change = on_file_change
        self.on_error = on_error
        self.observer: Optional[Observer] = None
        self.handler: Optional[ProjectFileHandler] = None
        self._is_running = False
        self._file_hashes: Dict[str, str] = {}
        self._last_sync_time = 0

        if not WATCHDOG_AVAILABLE:
            print("[FileWatcher] Warning: watchdog not installed. File watching disabled.")

    def start(self) -> bool:
        """启动文件监听"""
        if not WATCHDOG_AVAILABLE:
            print("[FileWatcher] Cannot start: watchdog not available")
            return False

        if self._is_running:
            print("[FileWatcher] Already running")
            return True

        try:
            if not self.project_path.exists():
                print(f"[FileWatcher] Project path does not exist: {self.project_path}")
                return False

            self.observer = Observer()
            self.handler = ProjectFileHandler(self)
            self.observer.schedule(
                self.handler,
                str(self.project_path),
                recursive=True
            )
            self.observer.start()
            self._is_running = True

            self._initial_sync()

            print(f"[FileWatcher] Started watching: {self.project_path}")
            return True

        except Exception as e:
            print(f"[FileWatcher] Failed to start: {e}")
            if self.on_error:
                self.on_error(e)
            return False

    def stop(self):
        """停止文件监听"""
        if self.observer:
            self.observer.stop()
            self.observer.join(timeout=5)
            self.observer = None
            self._is_running = False
            print(f"[FileWatcher] Stopped watching: {self.project_path}")

    def _initial_sync(self):
        """初始全量同步"""
        print("[FileWatcher] Performing initial sync...")
        count = 0

        for root, dirs, files in os.walk(self.project_path):
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS and not d.startswith('.')]

            for file in files:
                file_path = os.path.join(root, file)

                if not self.handler.should_process(file_path):
                    continue

                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()

                    file_hash = hashlib.md5(content.encode()).hexdigest()
                    self._file_hashes[file_path] = file_hash

                    change_event = FileChangeEvent(
                        event_type='sync',
                        file_path=file_path,
                        content=content,
                        language=self.handler._detect_language(file_path),
                        timestamp=time.time()
                    )

                    if self.on_file_change:
                        self.on_file_change(change_event)

                    count += 1

                except Exception:
                    continue

        self._last_sync_time = time.time()
        print(f"[FileWatcher] Initial sync complete: {count} files")

    def sync_changes(self) -> List[FileChangeEvent]:
        """获取所有变更"""
        changes = []

        if not self.project_path.exists():
            return changes

        for root, dirs, files in os.walk(self.project_path):
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

            for file in files:
                file_path = os.path.join(root, file)

                if not self.handler.should_process(file_path):
                    continue

                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()

                    file_hash = hashlib.md5(content.encode()).hexdigest()

                    if file_path not in self._file_hashes:
                        changes.append(FileChangeEvent(
                            event_type='created',
                            file_path=file_path,
                            content=content,
                            language=self.handler._detect_language(file_path)
                        ))
                    elif self._file_hashes[file_path] != file_hash:
                        changes.append(FileChangeEvent(
                            event_type='modified',
                            file_path=file_path,
                            content=content,
                            language=self.handler._detect_language(file_path)
                        ))

                    self._file_hashes[file_path] = file_hash

                except Exception:
                    continue

        for old_path in list(self._file_hashes.keys()):
            if not os.path.exists(old_path):
                changes.append(FileChangeEvent(
                    event_type='deleted',
                    file_path=old_path
                ))
                del self._file_hashes[old_path]

        self._last_sync_time = time.time()
        return changes

    def is_running(self) -> bool:
        """检查是否正在运行"""
        return self._is_running

    def get_watched_path(self) -> str:
        """获取监听路径"""
        return str(self.project_path)

    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            "is_running": self._is_running,
            "project_path": str(self.project_path),
            "tracked_files": len(self._file_hashes),
            "last_sync": self._last_sync_time
        }


class MultiProjectWatcher:
    """多项目监听管理器"""

    def __init__(self):
        self.watchers: Dict[int, ProjectFileWatcher] = {}
        self._lock = threading.Lock()

    def add_project(
        self,
        project_id: int,
        project_path: str,
        on_file_change: Callable[[int, FileChangeEvent], None],
        on_error: Callable[[Exception], None] = None
    ) -> bool:
        """添加项目监听"""
        with self._lock:
            if project_id in self.watchers:
                print(f"[MultiWatcher] Project {project_id} already watching")
                return False

            def wrapper(event: FileChangeEvent):
                on_file_change(project_id, event)

            watcher = ProjectFileWatcher(
                project_path=project_path,
                on_file_change=wrapper,
                on_error=on_error
            )

            if watcher.start():
                self.watchers[project_id] = watcher
                return True
            return False

    def remove_project(self, project_id: int):
        """移除项目监听"""
        with self._lock:
            if project_id in self.watchers:
                self.watchers[project_id].stop()
                del self.watchers[project_id]

    def stop_all(self):
        """停止所有监听"""
        with self._lock:
            for watcher in self.watchers.values():
                watcher.stop()
            self.watchers.clear()

    def get_active_count(self) -> int:
        """获取活跃监听数量"""
        return len(self.watchers)

    def get_all_stats(self) -> Dict:
        """获取所有项目统计"""
        return {
            project_id: watcher.get_stats()
            for project_id, watcher in self.watchers.items()
        }


multi_watcher_global: Optional[MultiProjectWatcher] = None

def get_multi_project_watcher() -> MultiProjectWatcher:
    global multi_watcher_global
    if multi_watcher_global is None:
        multi_watcher_global = MultiProjectWatcher()
    return multi_watcher_global
