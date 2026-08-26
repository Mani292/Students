import re
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from app.models.all_models import AIConversation, AIMessage, User
from app.services.ai_provider import get_ai_provider
from app.services.ai_tools import (
    get_attendance_summary_tool,
    get_permission_status_tool,
    get_student_profile_tool,
    search_university_knowledge_tool,
)


INJECTION_PATTERNS = (
    r"ignore\s+(all\s+)?previous instructions",
    r"reveal\s+(the\s+)?system prompt",
    r"show\s+(me\s+)?another student",
    r"access\s+someone else",
    r"bypass\s+(security|authorization|rbac)",
)


def _is_unsafe(message: str) -> bool:
    normalized = message.lower()
    return any(re.search(pattern, normalized) for pattern in INJECTION_PATTERNS)


def _conversation(db: Session, user: User, conversation_id: Optional[int], message: str) -> AIConversation:
    if conversation_id:
        conversation = db.query(AIConversation).filter(
            AIConversation.id == conversation_id,
            AIConversation.user_id == user.id,
        ).first()
        if not conversation:
            raise ValueError("Conversation not found")
    else:
        conversation = AIConversation(user_id=user.id, title=message[:80])
        db.add(conversation)
        db.flush()
    return conversation


def _route_tool(message: str, user: User, db: Session) -> Tuple[str, Any, List[Dict[str, Any]]]:
    normalized = message.lower()
    asks_for_policy = any(term in normalized for term in ("policy", "requirement", "minimum", "eligibility"))
    asks_for_personal_attendance = any(term in normalized for term in ("my attendance", "attendance percentage", "attendance summary"))
    if (asks_for_personal_attendance or "my classes" in normalized) and not asks_for_policy:
        return "get_attendance_summary_tool", get_attendance_summary_tool(user, db), []
    if "profile" in normalized or "cgpa" in normalized or "roll" in normalized:
        return "get_student_profile_tool", get_student_profile_tool(user, db), []
    if "permission" in normalized or "leave" in normalized:
        return "get_permission_status_tool", get_permission_status_tool(user, db), []

    results = search_university_knowledge_tool(message, db)
    sources = [{"id": item["id"], "title": item["title"], "category": item["category"], "source": item["source"], "score": item["score"]} for item in results]
    return "search_university_knowledge_tool", results, sources


def run_chat(
    message: str,
    user: User,
    db: Session,
    conversation_id: Optional[int] = None,
) -> Tuple[Optional[int], str, List[str], List[Dict[str, Any]]]:
    conversation = _conversation(db, user, conversation_id, message)
    db.add(AIMessage(conversation_id=conversation.id, sender="user", content=message))

    if _is_unsafe(message):
        response = "I can only access information allowed for your account. I cannot reveal another student's data or bypass security controls."
        tools_used: List[str] = []
        sources: List[Dict[str, Any]] = []
    else:
        tool_name, tool_result, sources = _route_tool(message, user, db)
        tools_used = [tool_name]
        if tool_name == "get_attendance_summary_tool":
            response = _format_attendance(tool_result)
        elif tool_name == "get_student_profile_tool":
            response = _format_profile(tool_result)
        elif tool_name == "get_permission_status_tool":
            response = _format_permissions(tool_result)
        elif tool_result:
            response = "Based on verified university sources:\n\n" + "\n\n".join(
                f"[{item['title']}] {item['content']}" for item in tool_result
            )
        else:
            response = "I couldn't find this in the university knowledge base."

        generated = get_ai_provider().generate(
            "You are a university assistant. Rewrite only the verified context into a concise answer. "
            "Never invent policies, private data, or citations.",
            f"Question: {message}\nVerified context: {response}",
        )
        if generated:
            response = generated
        if sources:
            citations = "\n\nSources:\n" + "\n".join(
                f"- {source['title']} ({source['source']})" for source in sources
            )
            if "Sources:" not in response:
                response = response.rstrip() + citations

    db.add(AIMessage(
        conversation_id=conversation.id,
        sender="assistant",
        content=response,
        tool_calls={"tools": tools_used, "sources": sources},
    ))
    db.commit()
    return conversation.id, response, tools_used, sources


def _format_attendance(data: Dict[str, Any]) -> str:
    if "error" in data:
        return data["error"]
    return f"Your current attendance summary:\nTotal Classes: {data['total_classes']}\nAttended: {data['classes_attended']}\nPercentage: {data['attendance_percentage']}%\nStatus: {data['status']}"


def _format_profile(data: Dict[str, Any]) -> str:
    if "error" in data:
        return data["error"]
    return f"Student Profile for {data['full_name']} (Roll: {data['roll_number']}):\nDepartment: {data['department']}\nYear/Sem: {data['year']}/{data['semester']}\nCGPA: {data['cgpa']}\nSkills: {', '.join(data['skills'])}"


def _format_permissions(data: List[Dict[str, Any]]) -> str:
    if not data:
        return "You have no active or historical leave/permission requests."
    return "Your permission requests:\n" + "\n".join(
        f"- ID #{item['id']}: {item['reason']} ({item['status']})" for item in data
    )