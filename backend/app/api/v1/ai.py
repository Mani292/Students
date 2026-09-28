from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.all_models import AIConversation, AIMessage, User
from app.schemas.ai_schemas import AIChatRequest, AIChatResponse, LearningPathRequest, LearningPathResponse
from app.core.rbac import get_current_user
from app.services.ai_orchestrator import run_chat

router = APIRouter(prefix="/ai", tags=["AI Copilot & Learning Hub"])

@router.post("/chat", response_model=AIChatResponse)
def ai_copilot_chat(
    req: AIChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if len(req.message.strip()) < 2:
        raise HTTPException(status_code=422, detail="Message must contain at least two characters")
    try:
        conversation_id, response_text, tools_used, sources = run_chat(
            req.message.strip(), current_user, db, req.conversation_id
        )
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return AIChatResponse(
        conversation_id=conversation_id,
        response=response_text,
        sources=sources,
        tools_used=tools_used,
    )


@router.get("/conversations/{conversation_id}/messages")
def get_conversation_messages(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conversation = db.query(AIConversation).filter(
        AIConversation.id == conversation_id,
        AIConversation.user_id == current_user.id,
    ).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return db.query(AIMessage).filter(
        AIMessage.conversation_id == conversation.id
    ).order_by(AIMessage.timestamp.asc()).all()

@router.post("/learning-path", response_model=LearningPathResponse)
def generate_learning_path(
    req: LearningPathRequest,
    current_user: User = Depends(get_current_user)
):
    subject = req.subject
    roadmap = [
        {"step": 1, "title": f"Fundamentals of {subject}", "description": "Core concepts, syntax, and foundational theory."},
        {"step": 2, "title": "Intermediate Operations & Data Processing", "description": "Hands-on data structures, OOP principles, and key libraries."},
        {"step": 3, "title": "Advanced Application Building", "description": "Full-stack integration, APIs, and production deployment best practices."},
        {"step": 4, "title": "Capstone Project & Interview Prep", "description": "Build a demonstrable university project and solve technical interview questions."}
    ]
    resources = [
        {"type": "Documentation", "title": f"Official {subject} Documentation", "url": "https://docs.python.org/3/"},
        {"type": "Course", "title": f"University Approved {subject} Interactive Modules", "url": "https://ocw.mit.edu"},
        {"type": "Practice", "title": f"{subject} Problem Set & Quiz System", "url": "https://leetcode.com"}
    ]

    return LearningPathResponse(
        subject=subject,
        roadmap=roadmap,
        recommended_resources=resources
    )

# --- Learning Tracks & Self-Learning Workflows ---

@router.get("/tracks")
def list_learning_tracks(db: Session = Depends(get_db)):
    from app.models.all_models import LearningTrack
    return db.query(LearningTrack).filter(LearningTrack.is_active == True).all()

@router.get("/tracks/{track_id}/resources")
def list_track_resources(track_id: int, db: Session = Depends(get_db)):
    from app.models.all_models import LearningResource
    return db.query(LearningResource).filter(LearningResource.track_id == track_id).order_by(LearningResource.sequence_order.asc()).all()

@router.get("/progress")
def get_student_learning_progress(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from app.models.all_models import StudentProgress, Student
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        return []
    return db.query(StudentProgress).filter(StudentProgress.student_id == student.id).all()
