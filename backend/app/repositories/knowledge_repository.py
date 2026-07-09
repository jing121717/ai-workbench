from sqlalchemy.orm import Session
from backend.app.models.user import Document
from typing import Optional


class KnowledgeRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_document(
        self, user_id: int, title: str, file_name: str = "", file_size: int = 0
    ) -> Document:
        doc = Document(user_id=user_id, title=title, file_name=file_name, file_size=file_size)
        self.db.add(doc)
        self.db.commit()
        self.db.refresh(doc)
        return doc

    def get_document(self, user_id: int, doc_id: int) -> Document | None:
        return (
            self.db.query(Document)
            .filter(Document.id == doc_id, Document.user_id == user_id)
            .first()
        )

    def list_documents(self, user_id: int, skip: int = 0, limit: int = 20) -> tuple[list[Document], int]:
        query = self.db.query(Document).filter(Document.user_id == user_id)
        total = query.count()
        results = query.order_by(Document.created_at.desc()).offset(skip).limit(limit).all()
        return results, total

    def update_document_status(self, doc_id: int, status: str, chunk_count: int = 0) -> None:
        doc = self.db.query(Document).filter(Document.id == doc_id).first()
        if doc:
            doc.status = status
            doc.chunk_count = chunk_count
            self.db.commit()

    def delete_document(self, user_id: int, doc_id: int) -> bool:
        doc = self.get_document(user_id, doc_id)
        if not doc:
            return False
        self.db.delete(doc)
        self.db.commit()
        return True
