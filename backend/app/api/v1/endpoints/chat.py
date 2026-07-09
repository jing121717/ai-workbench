import json
import asyncio
from fastapi import APIRouter, Depends, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.schemas.chat import ChatSessionCreate, ChatSessionResponse, StreamChatRequest
from backend.app.services.chat_service import ChatService
from backend.app.core.security import decode_token
from backend.app.core.exceptions import NotFoundError

router = APIRouter(prefix="/chat", tags=["对话"])


def get_current_user_id(authorization: str = None) -> int:
    if not authorization:
        return 1
    if authorization.startswith("Bearer "):
        token = authorization[7:]
    else:
        token = authorization
    payload = decode_token(token)
    return int(payload.get("sub", 1))


@router.post("/sessions", response_model=ChatSessionResponse)
async def create_session(
    req: ChatSessionCreate,
    db: Session = Depends(get_db),
    authorization: str = None,
):
    user_id = get_current_user_id(authorization)
    svc = ChatService(db)
    session = svc.create_session(user_id, req.title)
    return ChatSessionResponse(
        id=session.id, user_id=session.user_id, title=session.title,
        created_at=session.created_at, updated_at=session.updated_at
    )


@router.get("/sessions")
async def list_sessions(
    db: Session = Depends(get_db),
    authorization: str = None,
):
    user_id = get_current_user_id(authorization)
    svc = ChatService(db)
    return svc.list_sessions(user_id)


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: int,
    db: Session = Depends(get_db),
    authorization: str = None,
):
    user_id = get_current_user_id(authorization)
    svc = ChatService(db)
    ok = svc.delete_session(user_id, session_id)
    if not ok:
        raise NotFoundError("会话不存在")
    return {"message": "删除成功"}


@router.get("/sessions/{session_id}/messages")
async def list_messages(
    session_id: int,
    db: Session = Depends(get_db),
    authorization: str = None,
):
    user_id = get_current_user_id(authorization)
    svc = ChatService(db)
    messages = svc.list_messages(user_id, session_id)
    if messages is None:
        raise NotFoundError("会话不存在")
    return messages


@router.post("/stream")
async def stream_chat(
    req: StreamChatRequest,
    db: Session = Depends(get_db),
    authorization: str = None,
):
    user_id = get_current_user_id(authorization)
    svc = ChatService(db)

    async def event_generator():
        for item in svc.stream_chat(user_id, req.session_id, req.message):
            event = item.get("event", "message")
            data = item.get("data", {})
            if event == "metadata":
                yield f"event: metadata\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"
            elif event == "token":
                content = data.get("content", "")
                yield f"data: {json.dumps({'content': content}, ensure_ascii=False)}\n\n"
            elif event == "sources":
                yield f"event: sources\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"
            elif event == "done":
                yield f"event: done\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"
            await asyncio.sleep(0)

    return StreamingResponse(event_generator(), media_type="text/event-stream")
