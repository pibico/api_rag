"""
Documents router - Document upload, indexing, and management
Optimized for Markdown documents
"""
import os
import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status, BackgroundTasks
from sqlalchemy.orm import Session

from app.models import (
    User,
    Document as DocumentModel,
    DocumentSchema,
    DocumentUploadResponse,
    get_db,
)
from app.services import get_current_active_user, leann_service
from app.config import settings

router = APIRouter()


def index_document_background(document_id: int, file_path: str, file_type: str, db_session):
    """Background task to index document"""
    try:
        # Get document from database
        document = db_session.query(DocumentModel).filter(DocumentModel.id == document_id).first()
        if not document:
            return

        # Update status
        document.status = "indexing"
        db_session.commit()

        # Build LEANN index
        result = leann_service.build_index(
            document_id=str(document_id),
            file_path=file_path,
            file_type=file_type
        )

        if result["status"] == "success":
            document.status = "ready"
            document.leann_index_id = str(document_id)
        else:
            document.status = "error"
            document.error_message = result.get("error", "Unknown error")

        db_session.commit()

    except Exception as e:
        document.status = "error"
        document.error_message = str(e)
        db_session.commit()


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: str = Form(None),
    db: Session = Depends(get_db)
):
    """Upload and index a document (Markdown preferred) - No authentication required"""

    # Validate file type
    allowed_types = ["application/pdf", "text/plain", "text/markdown", "text/md"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not supported. Allowed: PDF, TXT, MD (Markdown preferred)"
        )

    # Auto-generate title from filename if not provided
    if not title:
        title = os.path.splitext(file.filename)[0]

    # Generate unique filename
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(settings.upload_dir, unique_filename)

    # Save file
    try:
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving file: {str(e)}"
        )

    # Create document record without owner (public mode)
    document = DocumentModel(
        title=title,
        filename=file.filename,
        file_path=file_path,
        file_type=file.content_type,
        file_size=len(content),
        owner_id=None,  # No owner in public mode
        status="pending"
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    # Start background indexing
    background_tasks.add_task(
        index_document_background,
        document.id,
        file_path,
        file.content_type,
        db
    )

    return DocumentUploadResponse(
        document_id=document.id,
        filename=file.filename,
        status="pending",
        message="Document uploaded successfully. Indexing in progress."
    )


@router.get("/", response_model=List[DocumentSchema])
def list_documents(
    db: Session = Depends(get_db)
):
    """List all documents (public mode - no authentication)"""
    documents = db.query(DocumentModel).order_by(DocumentModel.created_at.desc()).all()
    return documents


@router.get("/{document_id}", response_model=DocumentSchema)
def get_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """Get document by ID (public mode - no authentication)"""
    document = db.query(DocumentModel).filter(
        DocumentModel.id == document_id
    ).first()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    return document


@router.delete("/{document_id}")
def delete_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """Delete document (public mode - no authentication)"""
    from app.models import ChatSession as ChatSessionModel

    document = db.query(DocumentModel).filter(
        DocumentModel.id == document_id
    ).first()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    # Delete related chat sessions first
    try:
        chat_sessions = db.query(ChatSessionModel).filter(
            ChatSessionModel.document_id == document_id
        ).all()
        for session in chat_sessions:
            db.delete(session)
        db.flush()  # Flush but don't commit yet
    except Exception as e:
        print(f"Error deleting chat sessions: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting related chat sessions: {str(e)}"
        )

    # Delete file
    try:
        if os.path.exists(document.file_path):
            os.remove(document.file_path)
    except Exception as e:
        print(f"Error deleting file: {e}")

    # Delete LEANN index
    try:
        if document.leann_index_id:
            leann_service.delete_index(str(document.id))
    except Exception as e:
        print(f"Error deleting index: {e}")

    # Delete from database
    try:
        db.delete(document)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting document: {str(e)}"
        )

    return {"message": "Document deleted successfully"}
