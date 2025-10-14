"""
Chatbot API endpoints for AA Virtual platform.
Provides anonymous, privacy-focused chat functionality.
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import List, Optional
import hashlib
import time
import json
import logging

from app.db.database import get_db
from app.models.chatbot import ChatSession, ChatMessage, ChatResource, ChatAnalytics
from app.schemas.chatbot import (
    ChatSessionCreate, ChatSessionResponse, ChatMessageCreate, 
    ChatResponse, ChatResourceResponse, ChatAnalyticsResponse
)
from app.services.chatbot_service import ChatbotService
from app.core.config import settings

router = APIRouter()
security = HTTPBearer(auto_error=False)
logger = logging.getLogger(__name__)


def get_session_token(request: Request) -> str:
    """Generate or retrieve session token from request."""
    # Try to get from header first
    session_token = request.headers.get("X-Session-Token")
    
    if not session_token:
        # Generate from IP + User-Agent hash for anonymous users
        ip = request.client.host
        user_agent = request.headers.get("User-Agent", "")
        session_token = hashlib.sha256(f"{ip}:{user_agent}".encode()).hexdigest()[:32]
    
    return session_token


def rate_limit_check(request: Request, db: Session) -> bool:
    """Check if user has exceeded rate limits."""
    session_token = get_session_token(request)
    
    # Check recent message count
    recent_messages = db.query(ChatMessage).join(ChatSession).filter(
        ChatSession.session_token == session_token,
        ChatMessage.created_at > time.time() - 60,  # Last minute
        ChatMessage.role == "user"
    ).count()
    
    return recent_messages < settings.CHATBOT_RATE_LIMIT_PER_MINUTE


@router.post("/sessions", response_model=ChatSessionResponse)
async def create_chat_session(
    session_data: ChatSessionCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Create a new chat session."""
    session_token = get_session_token(request)
    
    # Check if session already exists
    existing_session = db.query(ChatSession).filter(
        ChatSession.session_token == session_token
    ).first()
    
    if existing_session and existing_session.is_active:
        return existing_session
    
    # Create new session
    chat_session = ChatSession(
        session_token=session_token,
        user_type=session_data.user_type,
        retain_history=session_data.retain_history,
        retention_days=session_data.retention_days
    )
    
    db.add(chat_session)
    db.commit()
    db.refresh(chat_session)
    
    logger.info(f"Created new chat session: {chat_session.id}")
    return chat_session


@router.get("/sessions/{session_id}", response_model=ChatSessionResponse)
async def get_chat_session(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Get chat session details."""
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.is_active == True
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    return session


@router.post("/sessions/{session_id}/messages", response_model=ChatResponse)
async def send_message(
    session_id: str,
    message_data: ChatMessageCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Send a message and get chatbot response."""
    start_time = time.time()
    
    # Rate limiting check
    if not rate_limit_check(request, db):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please wait before sending another message."
        )
    
    # Get session
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.is_active == True
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    # Check session message limit
    if session.message_count >= settings.CHATBOT_MAX_SESSION_MESSAGES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session message limit reached. Please start a new conversation."
        )
    
    try:
        # Save user message
        user_message = ChatMessage(
            session_id=session.id,
            role="user",
            content=message_data.content,
            message_type=message_data.message_type
        )
        db.add(user_message)
        
        # Process message with chatbot service
        chatbot_service = ChatbotService(db)
        response_data = await chatbot_service.process_message(
            session_id=session.id,
            user_message=message_data.content,
            session_context={
                "user_type": session.user_type,
                "message_count": session.message_count,
                "topics_discussed": session.topics_discussed or []
            }
        )
        
        # Save assistant response
        assistant_message = ChatMessage(
            session_id=session.id,
            role="assistant",
            content=response_data["content"],
            message_type="text",
            detected_intent=response_data.get("intent"),
            confidence_score=response_data.get("confidence"),
            quick_replies=response_data.get("quick_replies")
        )
        
        processing_time = int((time.time() - start_time) * 1000)
        assistant_message.processing_time_ms = processing_time
        
        db.add(assistant_message)
        
        # Update session
        session.message_count += 1
        if response_data.get("intent"):
            current_topics = session.topics_discussed or []
            if response_data["intent"] not in current_topics:
                current_topics.append(response_data["intent"])
                session.topics_discussed = current_topics
        
        db.commit()
        db.refresh(user_message)
        db.refresh(assistant_message)
        db.refresh(session)
        
        # Build response
        response = ChatResponse(
            message=assistant_message,
            session=session,
            suggestions=response_data.get("suggestions"),
            resources=response_data.get("resources")
        )
        
        logger.info(f"Processed message for session {session_id} in {processing_time}ms")
        return response
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error processing message: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing message"
        )


@router.get("/sessions/{session_id}/messages", response_model=List[ChatMessageResponse])
async def get_chat_history(
    session_id: str,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get chat message history for a session."""
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.is_active == True
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    messages = db.query(ChatMessage).filter(
        ChatMessage.session_id == session.id
    ).order_by(ChatMessage.created_at.desc()).limit(limit).all()
    
    return list(reversed(messages))


@router.get("/resources", response_model=List[ChatResourceResponse])
async def get_chat_resources(
    category: Optional[str] = None,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get available chat resources."""
    query = db.query(ChatResource).filter(ChatResource.is_active == True)
    
    if category:
        query = query.filter(ChatResource.category == category)
    
    resources = query.order_by(
        ChatResource.priority.desc(),
        ChatResource.usage_count.desc()
    ).limit(limit).all()
    
    return resources


@router.get("/analytics", response_model=List[ChatAnalyticsResponse])
async def get_chat_analytics(
    days: int = 7,
    db: Session = Depends(get_db)
):
    """Get chatbot analytics (admin only)."""
    # TODO: Add admin authentication
    analytics = db.query(ChatAnalytics).filter(
        ChatAnalytics.date >= time.time() - (days * 24 * 60 * 60)
    ).order_by(ChatAnalytics.date.desc()).all()
    
    return analytics


@router.post("/sessions/{session_id}/feedback")
async def submit_feedback(
    session_id: str,
    rating: int,
    feedback: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Submit feedback for a chat session."""
    if rating < 1 or rating > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rating must be between 1 and 5"
        )
    
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.is_active == True
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    session.satisfaction_rating = rating
    db.commit()
    
    logger.info(f"Received feedback: {rating}/5 for session {session_id}")
    return {"message": "Feedback submitted successfully"}


@router.delete("/sessions/{session_id}")
async def end_chat_session(
    session_id: str,
    db: Session = Depends(get_db)
):
    """End a chat session and optionally delete history."""
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.is_active == True
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    # Mark session as inactive
    session.is_active = False
    
    # If user didn't consent to history retention, delete messages
    if not session.retain_history:
        db.query(ChatMessage).filter(
            ChatMessage.session_id == session.id
        ).delete()
    
    db.commit()
    
    logger.info(f"Ended chat session: {session_id}")
    return {"message": "Chat session ended successfully"}
