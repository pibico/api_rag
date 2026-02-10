"""
Chat router - RAG-powered chat with documents
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
import time
import json

from app.models import (
    User,
    Document as DocumentModel,
    ChatSession as ChatSessionModel,
    ChatMessage as ChatMessageModel,
    ChatSessionCreate,
    ChatSessionSchema,
    QueryRequest,
    QueryResponse,
    get_db,
)
from app.services import get_current_active_user, leann_service, ollama_service

router = APIRouter()


@router.post("/sessions", response_model=ChatSessionSchema, status_code=status.HTTP_201_CREATED)
def create_chat_session(
    session_data: ChatSessionCreate,
    db: Session = Depends(get_db)
):
    """Create a new chat session (public mode - no authentication)"""
    # Determine if single or multi-document session
    doc_ids = []
    if session_data.document_ids:
        doc_ids = session_data.document_ids
    elif session_data.document_id:
        doc_ids = [session_data.document_id]
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either document_id or document_ids must be provided"
        )

    # Verify all documents exist and are ready
    documents = db.query(DocumentModel).filter(
        DocumentModel.id.in_(doc_ids)
    ).all()

    if len(documents) != len(doc_ids):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or more documents not found"
        )

    # Check all documents are ready
    not_ready = [doc for doc in documents if doc.status != "ready"]
    if not_ready:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Some documents are not ready: {', '.join([doc.title for doc in not_ready])}"
        )

    # Generate title
    if session_data.title:
        title = session_data.title
    elif len(documents) == 1:
        title = f"Chat about {documents[0].title}"
    else:
        title = f"Chat about {len(documents)} documents"

    # Create session (no user in public mode)
    session = ChatSessionModel(
        title=title,
        user_id=None,  # No user in public mode
        document_id=doc_ids[0],  # Always set to first document (for DB constraint)
        document_ids=json.dumps(doc_ids)
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    return session


@router.get("/sessions", response_model=List[ChatSessionSchema])
def list_chat_sessions(
    db: Session = Depends(get_db)
):
    """List all chat sessions (public mode - no authentication)"""
    sessions = db.query(ChatSessionModel).order_by(ChatSessionModel.updated_at.desc()).all()
    return sessions


@router.get("/sessions/{session_id}", response_model=ChatSessionSchema)
def get_chat_session(
    session_id: int,
    db: Session = Depends(get_db)
):
    """Get chat session with messages (public mode - no authentication)"""
    session = db.query(ChatSessionModel).filter(
        ChatSessionModel.id == session_id
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )

    return session


@router.delete("/sessions/{session_id}")
def delete_chat_session(
    session_id: int,
    db: Session = Depends(get_db)
):
    """Delete chat session (public mode - no authentication)"""
    session = db.query(ChatSessionModel).filter(
        ChatSessionModel.id == session_id
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )

    db.delete(session)
    db.commit()

    return {"message": "Chat session deleted successfully"}


@router.post("/query", response_model=QueryResponse)
def query_document(
    query_data: QueryRequest,
    db: Session = Depends(get_db)
):
    """Query document(s) using RAG (public mode - no authentication)"""
    # Track timing
    start_time = time.time()
    query_timestamp = datetime.now()

    # Verify session exists
    session = db.query(ChatSessionModel).filter(
        ChatSessionModel.id == query_data.session_id
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )

    # Get document IDs for this session
    doc_ids = []
    if session.document_ids:
        doc_ids = json.loads(session.document_ids)
    elif session.document_id:
        doc_ids = [session.document_id]
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session has no associated documents"
        )

    # Get all documents
    documents = db.query(DocumentModel).filter(
        DocumentModel.id.in_(doc_ids)
    ).all()

    # Check all documents are ready
    not_ready = [doc for doc in documents if doc.status != "ready"]
    if not_ready:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Some documents are not ready: {', '.join([doc.title for doc in not_ready])}"
        )

    # Search all documents and merge results
    all_results = []
    try:
        for document in documents:
            search_results = leann_service.search(
                document_id=str(document.id),
                query=query_data.query,
                top_k=query_data.top_k
            )
            # Add document title to each result for context
            for result in search_results:
                result["source_document"] = document.title
            all_results.extend(search_results)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching documents: {str(e)}"
        )

    # Filter by similarity threshold if specified
    from app.config import settings
    threshold = query_data.min_similarity if query_data.min_similarity is not None else settings.leann_default_similarity_threshold
    if threshold > 0.0:
        all_results = [r for r in all_results if r.get("score", 0) >= threshold]

    # Sort by score and take top_k results across all documents
    all_results.sort(key=lambda x: x.get("score", 0), reverse=True)
    top_results = all_results[:query_data.top_k]

    # Extract context chunks with source attribution
    context_chunks = [
        f"[From: {result['source_document']}] {result['text']}"
        for result in top_results
    ]

    # Get chat history
    chat_history = db.query(ChatMessageModel).filter(
        ChatMessageModel.session_id == session.id
    ).order_by(ChatMessageModel.created_at.desc()).limit(10).all()

    chat_history_formatted = [
        {"role": msg.role, "content": msg.content}
        for msg in reversed(chat_history)
    ]

    # Query Ollama
    try:
        answer = ollama_service.chat(
            query=query_data.query,
            context_chunks=context_chunks,
            chat_history=chat_history_formatted,
            system_instruction=query_data.system_instruction
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating response: {str(e)}"
        )

    # Save user message
    user_message = ChatMessageModel(
        session_id=session.id,
        role="user",
        content=query_data.query
    )
    db.add(user_message)

    # Save assistant message
    assistant_message = ChatMessageModel(
        session_id=session.id,
        role="assistant",
        content=answer,
        context_chunks=json.dumps(context_chunks)
    )
    db.add(assistant_message)

    db.commit()
    db.refresh(assistant_message)

    # Calculate timing
    response_timestamp = datetime.now()
    elapsed_time = time.time() - start_time

    return QueryResponse(
        answer=answer,
        context_chunks=context_chunks,
        session_id=session.id,
        message_id=assistant_message.id,
        query_timestamp=query_timestamp,
        response_timestamp=response_timestamp,
        elapsed_time=elapsed_time
    )
