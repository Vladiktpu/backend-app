from pydantic import BaseModel
from datetime import datetime
from typing import List

class MessageBase(BaseModel):
    content: str

class MessageCreate(MessageBase):
    pass

class Message(MessageBase):
    id: int
    session_id: int
    is_from_user: bool
    created_at: datetime

    class Config:
        from_attributes = True

class ChatSessionBase(BaseModel):
    pass

class ChatSessionCreate(ChatSessionBase):
    pass

class ChatSession(ChatSessionBase):
    id: int
    user_id: int
    created_at: datetime
    is_active: bool

    class Config:
        from_attributes = True

class ChatHistory(ChatSession):
    messages: List[Message]
