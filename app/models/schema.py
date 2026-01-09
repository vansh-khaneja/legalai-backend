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
    id: int
    email: str
    created_at: Optional[str] = None
