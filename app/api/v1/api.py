"""
API v1 router aggregation
"""
from fastapi import APIRouter

from app.api.v1.endpoints import auth, documents, chat, health

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(
    health.router,
    tags=["Health"]
)

api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"]
)

api_router.include_router(
    documents.router,
    prefix="/documents",
    tags=["Documents"]
)

api_router.include_router(
    chat.router,
    prefix="/chat",
    tags=["Chat"]
)
