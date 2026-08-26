from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.all_models import User, UserRole, KnowledgeDocument
from app.schemas.ai_schemas import (
    AIChatRequest, AIChatResponse, LearningPathRequest, LearningPathResponse,
    AIConceptExplainRequest, AIConceptExplainResponse,
    AIQuizRequest, AIQuizResponse, QuizQuestion,
    AIFlashcardsRequest, AIFlashcardsResponse, AIFlashcard,
    RAGDocCreate, RAGDocOut
)
from app.core.rbac import get_current_user, require_roles
from app.services.ai_tools import (
    get_student_profile_tool, get_attendance_summary_tool, get_permission_status_tool,
    get_timetable_tool, get_assignments_tool, get_service_requests_tool,
    get_campus_events_tool, get_library_books_tool, search_university_knowledge_tool
)

router = APIRouter(prefix="/ai", tags=["AI University Copilot & Learning Hub"])

@router.post("/chat", response_model=AIChatResponse)
def ai_copilot_chat(
    req: AIChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    msg = req.message.lower()
    tools_used = []
    sources = []

    if "attendance" in msg:
        tools_used.append("get_attendance_summary_tool")
        att = get_attendance_summary_tool(current_user, db)
        if "error" in att:
            response_text = att["error"]
        else:
            response_text = f"Your current attendance summary:\n- Total Classes: {att['total_classes']}\n- Attended: {att['classes_attended']}\n- Percentage: {att['attendance_percentage']}%\n- Status: {att['status']}"

    elif "timetable" in msg or "class today" in msg or "next class" in msg:
        tools_used.append("get_timetable_tool")
        classes = get_timetable_tool(current_user, db)
        if not classes:
            response_text = "You have no scheduled classes found for your enrolled semester today."
        else:
            cls_str = "\n".join([f"- {c['course_code']}: {c['course_title']} (Room {c['room']})" for c in classes])
            response_text = f"Your scheduled classes:\n{cls_str}"

    elif "assignment" in msg or "homework" in msg:
        tools_used.append("get_assignments_tool")
        assigns = get_assignments_tool(current_user, db)
        if not assigns:
            response_text = "No pending assignments found for your enrolled classes."
        else:
            a_str = "\n".join([f"- {a['title']} (Due: {a['due_date']}, Max Marks: {a['max_marks']})" for a in assigns])
            response_text = f"Your active assignments:\n{a_str}"

    elif "profile" in msg or "cgpa" in msg or "roll" in msg:
        tools_used.append("get_student_profile_tool")
        profile = get_student_profile_tool(current_user, db)
        if "error" in profile:
            response_text = profile["error"]
        else:
            response_text = f"Student Profile for {profile['full_name']} (Roll: {profile['roll_number']}):\n- Department: {profile['department']}\n- Year/Semester: {profile['year']}/{profile['semester']}\n- Current CGPA: {profile['cgpa']}\n- Registered Skills: {', '.join(profile['skills'])}"

    elif "permission" in msg or "my leave" in msg:
        tools_used.append("get_permission_status_tool")
        perms = get_permission_status_tool(current_user, db)
        if not perms:
            response_text = "You have no active or historical leave/permission requests."
        else:
            req_list = [f"- ID #{p['id']}: {p['reason']} ({p['status']}) on {p['created_at']}" for p in perms]
            response_text = "Your permission requests:\n" + "\n".join(req_list)

    elif "service" in msg or "certificate" in msg or "id card" in msg and "my" in msg:
        tools_used.append("get_service_requests_tool")
        srvs = get_service_requests_tool(current_user, db)
        if not srvs:
            response_text = "You have not submitted any service requests yet."
        else:
            s_list = [f"- {s['service_type']}: {s['status']} (Token: {s['verification_token']})" for s in srvs]
            response_text = "Your service requests:\n" + "\n".join(s_list)

    elif "event" in msg or "hackathon" in msg:
        tools_used.append("get_campus_events_tool")
        events = get_campus_events_tool(db)
        if not events:
            response_text = "No upcoming campus events currently scheduled."
        else:
            e_list = [f"- {e['title']} [{e['category']}] on {e['event_date']} at {e['venue']}" for e in events]
            response_text = "Upcoming University Events & Hackathons:\n" + "\n".join(e_list)

    elif "library" in msg or "book" in msg:
        tools_used.append("get_library_books_tool")
        query_kw = msg.replace("library", "").replace("book", "").strip() or "Computer"
        books = get_library_books_tool(query_kw, db)
        if not books:
            response_text = f"No library books found matching query '{query_kw}'."
        else:
            b_list = [f"- {b['title']} by {b['author']} ({b['available_copies']} available)" for b in books]
            response_text = "Library Catalog Results:\n" + "\n".join(b_list)

    else:
        # Fallback to RAG knowledge search
        tools_used.append("search_university_knowledge_tool")
        rag_results = search_university_knowledge_tool(req.message, db)
        if rag_results:
            sources = [{"title": r["title"], "category": r["category"]} for r in rag_results]
            matched_contents = "\n\n".join([f"[{r['title']}]: {r['content']}" for r in rag_results])
            response_text = f"Based on verified university documentation:\n\n{matched_contents}"
        else:
            response_text = f"I am your Smart University AI Assistant. I could not find specific university regulations matching '{req.message}'. Please contact your department coordinator or refine your question."

    return AIChatResponse(response=response_text, sources=sources, tools_used=tools_used)

@router.post("/learning-path", response_model=LearningPathResponse)
def generate_learning_path(
    req: LearningPathRequest,
    current_user: User = Depends(get_current_user)
):
    subject = req.subject
    roadmap = [
        {"step": 1, "title": f"Fundamentals of {subject}", "description": "Core concepts, syntax, and foundational theory."},
        {"step": 2, "title": "Data Structures & Core Algorithms", "description": "Hands-on data structures, OOP principles, and standard libraries."},
        {"step": 3, "title": "Scalable Application Building", "description": "Full-stack integration, APIs, automated testing, and production deployment."},
        {"step": 4, "title": "Capstone Project & Interview Readiness", "description": "Build a demonstrable university capstone project and solve technical interview questions."}
    ]
    resources = [
        {"type": "Documentation", "title": f"Official {subject} Technical Documentation", "url": "https://docs.python.org/3/"},
        {"type": "Course", "title": f"University Approved {subject} Interactive Modules", "url": "https://ocw.mit.edu"},
        {"type": "Practice", "title": f"{subject} Problem Set & Sandbox", "url": "https://leetcode.com"}
    ]

    return LearningPathResponse(
        subject=subject,
        roadmap=roadmap,
        recommended_resources=resources
    )

@router.post("/explain", response_model=AIConceptExplainResponse)
def explain_concept(
    req: AIConceptExplainRequest,
    current_user: User = Depends(get_current_user)
):
    concept = req.concept
    return AIConceptExplainResponse(
        concept=concept,
        explanation=f"{concept} is a foundational computer science concept crucial for scalable system design and efficient data handling. It ensures modularity, fault tolerance, and predictable runtime behavior.",
        key_points=[
            f"1. Core Definition: {concept} defines clear abstraction layers and predictable interfaces.",
            "2. Scalability: Enables decoupled components to scale independently without bottlenecking shared resources.",
            "3. Best Practice: Always write unit tests and enforce error boundaries when implementing."
        ],
        code_example=f"// Implementation Example for {concept}\nfunction execute{concept.replace(' ', '')}() {{\n    console.log('Executing verified pattern for {concept}');\n}}",
        practice_question=f"What is the primary architectural trade-off when implementing {concept} in high-throughput distributed systems?"
    )

@router.post("/quiz", response_model=AIQuizResponse)
def generate_quiz(
    req: AIQuizRequest,
    current_user: User = Depends(get_current_user)
):
    topic = req.topic
    questions = [
        QuizQuestion(
            id=1,
            question=f"What is the primary architectural advantage of using {topic}?",
            options=["High concurrency and decoupling", "Increased database latency", "Monolithic coupling", "Zero memory utilization"],
            correct_option_index=0,
            explanation=f"{topic} facilitates high concurrency, separation of concerns, and scalable microservice architectures."
        ),
        QuizQuestion(
            id=2,
            question=f"Which HTTP status code signifies that a resource created via {topic} API was successful?",
            options=["200 OK", "201 Created", "400 Bad Request", "500 Server Error"],
            correct_option_index=1,
            explanation="HTTP 201 Created is the standard REST status code returned upon successful entity creation."
        ),
        QuizQuestion(
            id=3,
            question="In anti-proxy attendance security, what does dynamic TOTP ensure?",
            options=["Permanent QR validity", "Single-use, time-windowed token validity to stop screenshot reuse", "Unrestricted manual entry", "No network connectivity required"],
            correct_option_index=1,
            explanation="Dynamic TOTP regenerates every 15-30 seconds, preventing proxy attendance via recorded screenshots or forwarded photos."
        ),
        QuizQuestion(
            id=4,
            question="What is the recommended minimum attendance percentage required by university policy for exam eligibility?",
            options=["50%", "65%", "75%", "90%"],
            correct_option_index=2,
            explanation="University regulations require a minimum of 75% attendance to qualify for end-semester examinations."
        )
    ]
    return AIQuizResponse(topic=topic, questions=questions[:req.num_questions])

@router.post("/flashcards", response_model=AIFlashcardsResponse)
def generate_flashcards(
    req: AIFlashcardsRequest,
    current_user: User = Depends(get_current_user)
):
    topic = req.topic
    cards = [
        AIFlashcard(
            id=1,
            category=topic,
            front=f"What is the main definition of {topic}?",
            back="An established pattern and technical framework used to solve computational and operational challenges reliably."
        ),
        AIFlashcard(
            id=2,
            category="Security & RBAC",
            front="What is Role-Based Access Control (RBAC)?",
            back="An authorization mechanism that restricts system access to authorized users based on their assigned roles (e.g. Student, Faculty, HOD, Admin)."
        ),
        AIFlashcard(
            id=3,
            category="AI & RAG",
            front="How does Retrieval-Augmented Generation (RAG) eliminate hallucinations?",
            back="By retrieving verified grounding passages from the university knowledge base before prompting the language model."
        )
    ]
    return AIFlashcardsResponse(topic=topic, cards=cards)

@router.get("/documents", response_model=List[RAGDocOut])
def list_rag_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.SUPER_ADMIN, UserRole.FACULTY, UserRole.HOD]))
):
    return db.query(KnowledgeDocument).all()

@router.post("/documents", response_model=RAGDocOut)
def add_rag_document(
    req: RAGDocCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.SUPER_ADMIN]))
):
    doc = KnowledgeDocument(
        title=req.title,
        category=req.category,
        content=req.content,
        source=req.source
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc
