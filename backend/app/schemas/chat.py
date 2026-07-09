from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ChatSessionCreate(BaseModel):
    title: str = "新会话"


class ChatSessionResponse(BaseModel):
    id: int
    user_id: int
    title: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ChatMessageCreate(BaseModel):
    role: str
    content: str


class ChatMessageResponse(BaseModel):
    id: int
    session_id: int
    role: str
    content: str
    sources: Optional[str] = "[]"
    created_at: datetime

    class Config:
        from_attributes = True


class StreamChatRequest(BaseModel):
    session_id: int | None = None
    message: str


class StreamMetaResponse(BaseModel):
    session_id: int
    session_title: str
