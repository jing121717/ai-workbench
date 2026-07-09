import os
from pathlib import Path
from fastapi import APIRouter, Depends, UploadFile, File, Header
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.schemas.knowledge import DocumentListResponse, DocumentUploadResponse
from backend.app.services.knowledge_service import KnowledgeService
from backend.app.core.exceptions import NotFoundError

router = APIRouter(prefix="/knowledge", tags=["知识库"])


def get_user_id(authorization: str = None) -> int:
    if not authorization:
        return 1
    if authorization.startswith("Bearer "):
        token = authorization[7:]
    else:
        token = authorization
    try:
        from backend.app.core.security import decode_token
        payload = decode_token(token)
        return int(payload.get("sub", 1))
    except Exception:
        return 1


@router.get("/documents", response_model=DocumentListResponse)
async def list_documents(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    authorization: str = None,
):
    user_id = get_user_id(authorization)
    svc = KnowledgeService(db)
    return svc.list_documents(user_id, skip, limit)


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    authorization: str = None,
):
    user_id = get_user_id(authorization)
    svc = KnowledgeService(db)

    content = await file.read()
    file_size = len(content)
    title = Path(file.filename).stem

    text_content = content.decode("utf-8", errors="ignore")

    result = svc.upload_document(user_id, title, text_content, file.filename, file_size)
    return DocumentUploadResponse(
        id=result["id"],
        title=result["title"],
        status=result["status"],
        chunk_count=result["chunk_count"],
        message=result["message"],
    )


@router.delete("/documents/{doc_id}")
async def delete_document(
    doc_id: int,
    db: Session = Depends(get_db),
    authorization: str = None,
):
    user_id = get_user_id(authorization)
    svc = KnowledgeService(db)
    ok = svc.delete_document(user_id, doc_id)
    if not ok:
        raise NotFoundError("文档不存在")
    return {"message": "删除成功"}
