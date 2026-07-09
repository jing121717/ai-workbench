import json
import time
from sqlalchemy.orm import Session
from backend.app.repositories.chat_repository import ChatRepository
from backend.app.services.rag_service import rag_service


class ChatService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = ChatRepository(db)

    def create_session(self, user_id: int, title: str):
        return self.repo.create_session(user_id, title)

    def list_sessions(self, user_id: int):
        sessions = self.repo.list_sessions(user_id)
        return [{"id": s.id, "user_id": s.user_id, "title": s.title,
                 "created_at": s.created_at.isoformat(), "updated_at": s.updated_at.isoformat()}
                for s in sessions]

    def rename_session(self, user_id: int, session_id: int, title: str):
        session = self.repo.get_session(user_id, session_id)
        if not session:
            return None
        return self.repo.rename_session(session, title)

    def delete_session(self, user_id: int, session_id: int) -> bool:
        session = self.repo.get_session(user_id, session_id)
        if not session:
            return False
        self.repo.delete_session(session)
        return True

    def list_messages(self, user_id: int, session_id: int):
        session = self.repo.get_session(user_id, session_id)
        if not session:
            return None
        messages = self.repo.list_messages(session_id)
        return [{
            "id": m.id, "session_id": m.session_id, "role": m.role,
            "content": m.content, "sources": m.sources,
            "created_at": m.created_at.isoformat()
        } for m in messages]

    def stream_chat(self, user_id: int, session_id: int | None, message: str):
        session = self.repo.get_session(user_id, session_id) if session_id else None
        if session is None:
            session = self.repo.create_session(user_id, title=message[:30] or "新会话")

        self.repo.create_message(session.id, "user", message)
        yield {"event": "metadata", "data": {"session_id": session.id, "session_title": session.title}}

        answer_parts: list[str] = []
        last_sources: list[dict] = []

        try:
            for item in rag_service.stream_answer(user_id, message):
                if item["event"] == "token":
                    answer_parts.append(item["data"]["content"])
                if item["event"] == "metadata":
                    last_sources = item["data"].get("sources", [])
                yield item
        except Exception as e:
            fallback = f"抱歉，AI 服务暂时不可用，请稍后重试。错误信息：{str(e)}"
            for ch in fallback:
                answer_parts.append(ch)
                yield {"event": "token", "data": {"content": ch}}
                time.sleep(0.01)

        answer_text = "".join(answer_parts)
        self.repo.create_message(session.id, "assistant", answer_text, sources=json.dumps(last_sources))
        yield {"event": "sources", "data": {"sources": last_sources}}
