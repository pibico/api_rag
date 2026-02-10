"""
Database models and schemas
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.config import settings
from app.models.database import Base, User, Document, ChatSession, ChatMessage
from app.models.schemas import (
    UserCreate, UserLogin, UserSchema, Token, TokenData,
    DocumentSchema, DocumentUploadResponse,
    ChatSessionCreate, ChatSessionSchema, ChatMessageSchema,
    QueryRequest, QueryResponse
)

# Create engine
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


__all__ = [
    "User", "Document", "ChatSession", "ChatMessage",
    "UserCreate", "UserLogin", "UserSchema", "Token", "TokenData",
    "DocumentSchema", "DocumentUploadResponse",
    "ChatSessionCreate", "ChatSessionSchema", "ChatMessageSchema",
    "QueryRequest", "QueryResponse",
    "get_db", "init_db"
]
