from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.all_models import User
from app.schemas.ai_schemas import AIChatRequest, AIChatResponse, LearningPathRequest, LearningPathResponse
from app.core.rbac import get_current_user
from app.services.ai_tools import (
    get_student_profile_tool, get_attendance_summary_tool, get_permission_status_tool, search_university_knowledge_tool
)

router = APIRouter(prefix="/ai", tags=["AI Copilot & Learning Hub"])

@router.post("/chat", response_model=AIChatResponse)
def ai_copilot_chat(
    req: AIChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    msg = req.message.lower()
    tools_used = []
    sources = []

    if "my attendance" in msg or "classes" in msg:
        tools_used.append("get_attendance_summary_tool")
        att = get_attendance_summary_tool(current_user, db)
        if "error" in att:
            response_text = att["error"]
        else:
            response_text = f"Your current attendance summary:\nTotal Classes: {att['total_classes']}\nAttended: {att['classes_attended']}\nPercentage: {att['attendance_percentage']}%\nStatus: {att['status']}"

    elif "profile" in msg or "cgpa" in msg or "roll" in msg:
        tools_used.append("get_student_profile_tool")
        profile = get_student_profile_tool(current_user, db)
        if "error" in profile:
            response_text = profile["error"]
        else:
            response_text = f"Student Profile for {profile['full_name']} (Roll: {profile['roll_number']}):\nDepartment: {profile['department']}\nYear/Sem: {profile['year']}/{profile['semester']}\nCGPA: {profile['cgpa']}\nSkills: {', '.join(profile['skills'])}"

    elif "permission" in msg or "my leave" in msg:
        tools_used.append("get_permission_status_tool")
        perms = get_permission_status_tool(current_user, db)
        if not perms:
            response_text = "You have no active or historical leave/permission requests."
        else:
            req_list = [f"- ID #{p['id']}: {p['reason']} ({p['status']})" for p in perms]
            response_text = "Your permission requests:\n" + "\n".join(req_list)

    else:
        # Fallback to RAG knowledge search
        tools_used.append("search_university_knowledge_tool")
        rag_results = search_university_knowledge_tool(req.message, db)
        if rag_results:
            sources = [{"title": r["title"], "category": r["category"]} for r in rag_results]
            matched_contents = "\n\n".join([f"[{r['title']}]: {r['content']}" for r in rag_results])
            response_text = f"Based on university documentation:\n\n{matched_contents}"
        else:
            response_text = f"I am your Smart University AI Assistant. I could not find specific university policy details matching '{req.message}'. Please check with your department coordinator or refine your query."

    return AIChatResponse(response=response_text, sources=sources, tools_used=tools_used)

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
