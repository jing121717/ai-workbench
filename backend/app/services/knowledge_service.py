import os
from pathlib import Path
from sqlalchemy.orm import Session
from backend.app.repositories.knowledge_repository import KnowledgeRepository
from backend.app.services.rag_service import rag_service


class KnowledgeService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = KnowledgeRepository(db)

    def list_documents(self, user_id: int, skip: int = 0, limit: int = 20):
        docs, total = self.repo.list_documents(user_id, skip, limit)
        return {
            "total": total,
            "results": [
                {
                    "id": d.id, "user_id": d.user_id, "title": d.title,
                    "file_name": d.file_name, "file_size": d.file_size,
                    "chunk_count": d.chunk_count, "status": d.status,
                    "created_at": d.created_at.isoformat(),
                }
                for d in docs
            ],
        }

    def upload_document(self, user_id: int, title: str, content: str, file_name: str = "", file_size: int = 0) -> dict:
        doc = self.repo.create_document(user_id, title=title, file_name=file_name, file_size=file_size)
        try:
            rag_service.index_document(user_id, doc.id, content, title)
            chunk_count = len(content) // 500 + 1
            self.repo.update_document_status(doc.id, "completed", chunk_count)
            return {"id": doc.id, "title": title, "status": "completed", "chunk_count": chunk_count, "message": "文档处理成功"}
        except Exception as exc:
            self.repo.update_document_status(doc.id, "failed", 0)
            return {"id": doc.id, "title": title, "status": "failed", "chunk_count": 0, "message": f"处理失败：{exc}"}

    def delete_document(self, user_id: int, doc_id: int) -> bool:
        return self.repo.delete_document(user_id, doc_id)
