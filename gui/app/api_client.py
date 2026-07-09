"""
AI Workbench · 桌面客户端 API 客户端
封装所有 HTTP 请求，复用后端 FastAPI 所有接口
"""
import requests
from typing import Optional


class ApiClient:
    def __init__(self, base_url: str = "http://127.0.0.1:8000") -> None:
        self.base_url = base_url
        self.token: str = ""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    def _headers(self) -> dict:
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    # ── Auth ──────────────────────────────────────────────────────────────────
    def login(self, username: str, password: str) -> str:
        resp = self.session.post(
            f"{self.base_url}/api/v1/auth/login",
            json={"username": username, "password": password},
            headers={"Content-Type": "application/json"},
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        self.token = data["access_token"]
        return self.token

    # ── Chat Sessions ─────────────────────────────────────────────────────────
    def list_sessions(self) -> list[dict]:
        resp = self.session.get(f"{self.base_url}/api/v1/chat/sessions", headers=self._headers(), timeout=10)
        resp.raise_for_status()
        return resp.json()

    def create_session(self, title: str) -> dict:
        resp = self.session.post(
            f"{self.base_url}/api/v1/chat/sessions",
            json={"title": title},
            headers=self._headers(),
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def delete_session(self, session_id: int) -> None:
        resp = self.session.delete(
            f"{self.base_url}/api/v1/chat/sessions/{session_id}",
            headers=self._headers(),
            timeout=10,
        )
        resp.raise_for_status()

    def list_messages(self, session_id: int) -> list[dict]:
        resp = self.session.get(
            f"{self.base_url}/api/v1/chat/sessions/{session_id}/messages",
            headers=self._headers(),
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    # ── SSE Stream ─────────────────────────────────────────────────────────────
    def stream_chat(self, session_id: int | None, message: str):
        url = f"{self.base_url}/api/v1/chat/stream"
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        resp = self.session.post(
            url,
            json={"session_id": session_id, "message": message},
            headers=headers,
            stream=True,
            timeout=120,
        )
        resp.raise_for_status()
        return resp.iter_lines(decode_unicode=True)

    # ── Knowledge ─────────────────────────────────────────────────────────────
    def list_documents(self, skip: int = 0, limit: int = 100) -> dict:
        resp = self.session.get(
            f"{self.base_url}/api/v1/knowledge/documents",
            params={"skip": skip, "limit": limit},
            headers=self._headers(),
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def upload_document(self, file_path: str) -> dict:
        with open(file_path, "rb") as f:
            files = {"file": (file_path.split("/")[-1], f, "application/octet-stream")}
            data = {}
            headers = {}
            if self.token:
                headers["Authorization"] = f"Bearer {self.token}"
            resp = self.session.post(
                f"{self.base_url}/api/v1/knowledge/upload",
                files=files,
                data=data,
                headers=headers,
                timeout=120,
            )
        resp.raise_for_status()
        return resp.json()

    def delete_document(self, doc_id: int) -> None:
        resp = self.session.delete(
            f"{self.base_url}/api/v1/knowledge/documents/{doc_id}",
            headers=self._headers(),
            timeout=10,
        )
        resp.raise_for_status()

    # ── Code Projects ────────────────────────────────────────────────────────
    def list_code_projects(self) -> dict:
        resp = self.session.get(
            f"{self.base_url}/api/v1/code-projects/",
            headers=self._headers(),
            timeout=20,
        )
        resp.raise_for_status()
        return resp.json()

    def get_code_project(self, project_id: int) -> dict:
        resp = self.session.get(
            f"{self.base_url}/api/v1/code-projects/{project_id}",
            headers=self._headers(),
            timeout=20,
        )
        resp.raise_for_status()
        return resp.json()

    def list_code_units(self, project_id: int, unit_type: str | None = None, file_path: str | None = None) -> dict:
        params = {}
        if unit_type:
            params["unit_type"] = unit_type
        if file_path:
            params["file_path"] = file_path
        resp = self.session.get(
            f"{self.base_url}/api/v1/code-projects/{project_id}/units",
            params=params,
            headers=self._headers(),
            timeout=20,
        )
        resp.raise_for_status()
        return resp.json()

    def sync_code_project(self, project_id: int) -> dict:
        resp = self.session.post(
            f"{self.base_url}/api/v1/code-projects/{project_id}/sync",
            headers=self._headers(),
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json()

    def git_clone_project(self, url: str, local_path: str = "", branch: str = "main") -> dict:
        resp = self.session.post(
            f"{self.base_url}/api/v1/code-projects/git-clone",
            json={"url": url, "local_path": local_path or None, "branch": branch},
            headers=self._headers(),
            timeout=300,
        )
        resp.raise_for_status()
        return resp.json()

    def sync_file(self, file_path: str, content: str, language: str, project_id: int | None = None) -> dict:
        payload = {"file_path": file_path, "content": content, "language": language}
        if project_id is not None:
            payload["project_id"] = project_id
        resp = self.session.post(
            f"{self.base_url}/api/v1/ide/sync-file",
            json=payload,
            headers=self._headers(),
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json()

    def search_code(self, query: str, project_id: int | None = None, unit_type: str | None = None, language: str | None = None) -> dict:
        params = {"query": query}
        if project_id is not None:
            params["project_id"] = project_id
        if unit_type:
            params["unit_type"] = unit_type
        if language:
            params["language"] = language
        resp = self.session.get(
            f"{self.base_url}/api/v1/code-projects/search/",
            params=params,
            headers=self._headers(),
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()

    # ── Code AI ──────────────────────────────────────────────────────────────
    def analyze_code(self, code: str, language: str, analysis_type: str = "defect") -> dict:
        resp = self.session.post(
            f"{self.base_url}/api/v1/code-ai/analyze",
            json={"code": code, "language": language, "analysis_type": analysis_type},
            headers=self._headers(),
            timeout=120,
        )
        resp.raise_for_status()
        return resp.json()

    def refactor_code(self, code: str, language: str, refactor_type: str = "readability") -> dict:
        resp = self.session.post(
            f"{self.base_url}/api/v1/code-ai/refactor",
            json={"code": code, "language": language, "refactor_type": refactor_type},
            headers=self._headers(),
            timeout=120,
        )
        resp.raise_for_status()
        return resp.json()

    def generate_unit_test(self, code: str, language: str, framework: str = "pytest") -> dict:
        resp = self.session.post(
            f"{self.base_url}/api/v1/code-ai/unit-test",
            json={"code": code, "language": language, "framework": framework},
            headers=self._headers(),
            timeout=120,
        )
        resp.raise_for_status()
        return resp.json()

    # ── Snippets ─────────────────────────────────────────────────────────────
    def list_snippets(self, keyword: str = "", category: str = "", language: str = "") -> dict:
        params = {}
        if keyword:
            params["keyword"] = keyword
        if category:
            params["category"] = category
        if language:
            params["language"] = language
        resp = self.session.get(
            f"{self.base_url}/api/v1/snippets/",
            params=params,
            headers=self._headers(),
            timeout=20,
        )
        resp.raise_for_status()
        return resp.json()

    def get_snippet(self, snippet_id: int) -> dict:
        resp = self.session.get(
            f"{self.base_url}/api/v1/snippets/{snippet_id}",
            headers=self._headers(),
            timeout=20,
        )
        resp.raise_for_status()
        return resp.json()

    def create_snippet(self, title: str, content: str, language: str = "python", category: str = "utility") -> dict:
        resp = self.session.post(
            f"{self.base_url}/api/v1/snippets/",
            json={
                "title": title,
                "content": content,
                "language": language,
                "category": category,
                "tags": [],
                "description": "",
            },
            headers=self._headers(),
            timeout=20,
        )
        resp.raise_for_status()
        return resp.json()

    # ── Health ────────────────────────────────────────────────────────────────
    def health_check(self) -> bool:
        try:
            resp = self.session.get(f"{self.base_url}/api/health", timeout=5)
            return resp.status_code == 200
        except Exception:
            return False
