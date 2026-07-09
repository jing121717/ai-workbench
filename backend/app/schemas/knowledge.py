from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class DocumentResponse(BaseModel):
    id: int
    user_id: int
    title: str
    file_name: Optional[str] = None
    file_size: int = 0
    chunk_count: int = 0
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentUploadResponse(BaseModel):
    id: int
    title: str
    status: str
    chunk_count: int
    message: str


class DocumentListResponse(BaseModel):
    total: int
    results: list[DocumentResponse]
