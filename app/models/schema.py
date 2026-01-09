from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class IngestRequest(BaseModel):
    case_type: str
    date: str

class IngestResponse(BaseModel):
    message: str
    chunks: int
    pdf_url: str

class QueryRequest(BaseModel):
    query: str

class Source(BaseModel):
    score: float
    text: str
    case_types: str
    file_id: str
    date: str
    pdf_url: Optional[str] = None

class QueryResponse(BaseModel):
    response: str
    sources: List[Source]

# User schemas
class CreateUserRequest(BaseModel):
    email: str

class UserResponse(BaseModel):
    id: str  # UUID as string
    email: str
    created_at: Optional[str] = None

# Chat schemas
class ChatResponse(BaseModel):
    id: str  # UUID as string
    user_id: str  # UUID as string
    created_at: Optional[str] = None

class ChatListResponse(BaseModel):
    chats: List[Dict[str, str]]  # List of {"id": str, "created_at": str}

class AddMessageRequest(BaseModel):
    chat_id: str
    role: str  # 'user' or 'assistant'
    content: str

class MessageResponse(BaseModel):
    chat_id: str
    role: str
    content: str
    created_at: Optional[str] = None

class ChatMessagesResponse(BaseModel):
    chat_id: str
    messages: List[Dict[str, str]]  # List of {"role": str, "content": str, "created_at": str}

class MessageListResponse(BaseModel):
    messages: List[Dict[str, str]]  # List of {"role": str, "content": str, "created_at": str}

class MessageListResponse(BaseModel):
    chat_id: str
    messages: List[Dict[str, str]]  # [{"role": str, "content": str, "created_at": str}, ...]
    