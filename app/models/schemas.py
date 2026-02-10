"""
Pydantic schemas for API requests and responses
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


# User schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserSchema(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


# Document schemas
class DocumentBase(BaseModel):
    title: str


class DocumentUploadResponse(BaseModel):
    document_id: int
    filename: str
    status: str
    message: str


class DocumentSchema(DocumentBase):
    id: int
    filename: str
    file_type: str
    file_size: int
    status: str
    error_message: Optional[str] = None
    leann_index_id: Optional[str] = None
    owner_id: Optional[int] = None  # Nullable for public mode
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Chat schemas
class ChatSessionCreate(BaseModel):
    title: Optional[str] = None
    document_id: Optional[int] = None
    document_ids: Optional[List[int]] = None


class ChatMessageSchema(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class ChatSessionSchema(BaseModel):
    id: int
    title: str
    user_id: Optional[int] = None  # Nullable for public mode
    document_id: int
    document_ids: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    messages: List[ChatMessageSchema] = []

    class Config:
        from_attributes = True


class QueryRequest(BaseModel):
    session_id: int
    query: str
    top_k: int = Field(default=5, ge=1, le=20)
    min_similarity: Optional[float] = Field(None, description="Minimum similarity threshold (0.0-1.0)", ge=0.0, le=1.0)
    system_instruction: Optional[str] = Field(None, description="Custom system instruction for this query")


class QueryResponse(BaseModel):
    answer: str
    context_chunks: List[str]
    session_id: int
    message_id: int
    query_timestamp: datetime
    response_timestamp: datetime
    elapsed_time: float
