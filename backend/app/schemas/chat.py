from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class ChatSessionCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    model: str = "gemini-2.5-flash"


class ChatSessionResponse(BaseModel):
    id: str
    user_id: str
    title: str
    model: str
    created_at: datetime

    class Config:
        from_attributes = True


class ChatMessageCreate(BaseModel):
    role: str = Field(..., min_length=1, max_length=20)
    content: str = Field(..., min_length=1)


class ChatMessageResponse(BaseModel):
    id: str
    session_id: str
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class ChatSendRequest(BaseModel):
    session_id: str
    message: str = Field(..., min_length=1)


class ChatSendResponse(BaseModel):
    response: str


class ChatSessionDetails(BaseModel):
    session: ChatSessionResponse
    messages: List[ChatMessageResponse]
