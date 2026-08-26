from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.all_models import User, Student
from app.schemas.career_schemas import (
    JobSearchRequest, JobListingOut, JobMatchRequest, JobMatchResponse,
    ResumeAnalysisRequest, ResumeAnalysisResponse,
    CoverLetterRequest, CoverLetterResponse,
    ProjectMentorRequest, ProjectMentorResponse
)
from app.core.rbac import get_current_user

router = APIRouter(prefix="/career-project", tags=["AI Career Engine & Project Lab Workspace"])

MOCK_JOBS = [
    {
        "id": 1,
        "title": "Full-Stack Software Engineer Intern",
        "company": "TechCorp Innovations",
        "location": "Remote / San Francisco",
        "job_type": "Internship",
        "stipend_or_salary": "$3,500 / month",
        "required_skills": ["Python", "React", "FastAPI", "SQL", "Docker", "TypeScript"],
        "description": "Build high-throughput web applications, design RESTful microservices, and collaborate in an agile engineering team."
    },
    {
        "id": 2,
        "title": "AI & Machine Learning Engineer Associate",
        "company": "DataMind AI Research",
        "location": "New York, NY (Hybrid)",
        "job_type": "Full-time",
        "stipend_or_salary": "$95,000 / year",
        "required_skills": ["Python", "PyTorch", "RAG", "Embeddings", "FastAPI", "SQL"],
        "description": "Develop and evaluate production LLM systems, implement vector retrieval pipelines, and design automated guardrails."
    },
    {
        "id": 3,
        "title": "Cloud DevOps & Platform Engineer",
        "company": "Nexus Infrastructure Labs",
        "location": "Austin, TX (Remote)",
        "job_type": "Internship",
        "stipend_or_salary": "$3,200 / month",
        "required_skills": ["Docker", "Kubernetes", "Linux", "CI/CD", "Python", "AWS"],
        "description": "Maintain automated container pipelines, orchestrate Kubernetes clusters, and implement continuous observability."
    },
    {
        "id": 4,
        "title": "Cybersecurity & Identity Analyst",
        "company": "Aegis Cyber Defense",
        "location": "Boston, MA",
        "job_type": "Full-time",
        "stipend_or_salary": "$88,000 / year",
        "required_skills": ["Security", "JWT", "RBAC", "Python", "Cryptography", "Network"],
        "description": "Audit authentication architectures, conduct anti-proxy and vulnerability assessments, and enforce zero-trust policies."
    }
]

@router.get("/jobs", response_model=List[JobListingOut])
def get_jobs():
    return MOCK_JOBS

@router.post("/match-job", response_model=JobMatchResponse)
def match_job(req: JobMatchRequest):
    user_skills_lower = [s.lower() for s in req.student_skills]
    jd_lower = req.job_description.lower()

    skills_pool = [
        "Python", "React", "FastAPI", "Docker", "AWS", "SQL", "Kubernetes", "PyTorch",
        "TypeScript", "Security", "JWT", "Linux", "CI/CD", "Tailwind", "Git"
    ]

    matching = [s for s in req.student_skills if s.lower() in jd_lower]
    missing = [s for s in skills_pool if s.lower() in jd_lower and s.lower() not in user_skills_lower]

    total_reqs = max(len(matching) + len(missing), 1)
    score = min(round((len(matching) / total_reqs) * 100.0, 1), 100.0)

    recs = []
    if missing:
        recs.append(f"Fill critical skill gaps by completing a practical project using {', '.join(missing[:2])}.")
    if score >= 75.0:
        recs.append("Your skill profile is highly aligned. Highlight quantifiable university achievements in your resume.")
    else:
        recs.append("Enroll in the recommended AI Learning Hub modules to boost your match rating above 80%.")

    return JobMatchResponse(
        match_score=score,
        matching_skills=matching,
        missing_skills=missing,
        recommendations=recs
    )

@router.post("/analyze-resume", response_model=ResumeAnalysisResponse)
def analyze_resume(req: ResumeAnalysisRequest):
    text = req.resume_text
    skills_catalog = [
        "Python", "React", "FastAPI", "SQL", "Docker", "AWS", "TypeScript", "Git",
        "Machine Learning", "PyTorch", "Kubernetes", "CI/CD", "Linux", "C++", "Java"
    ]
    found = [s for s in skills_catalog if s.lower() in text.lower()]

    score = min(50.0 + len(found) * 4.0, 96.0)
    improvements = []
    if "docker" not in text.lower() and "container" not in text.lower():
        improvements.append("Add containerization & deployment experience (e.g. Docker, Docker Compose).")
    if "%" not in text and "improved" not in text.lower() and "reduced" not in text.lower():
        improvements.append("Quantify project outcomes (e.g., 'Reduced response latency by 40% and improved throughput').")
    if "testing" not in text.lower() and "pytest" not in text.lower():
        improvements.append("Highlight automated testing methodologies (unit tests, integration test suites).")
    if not improvements:
        improvements.append("Resume formatting is strong! Ensure GitHub repository links and demo URLs are active.")

    return ResumeAnalysisResponse(
        ats_score=score,
        extracted_skills=found,
        improvement_areas=improvements
    )

@router.post("/cover-letter", response_model=CoverLetterResponse)
def generate_cover_letter(req: CoverLetterRequest):
    skills_str = ", ".join(req.student_skills[:4])
    body = (
        f"Dear Hiring Team at {req.company_name},\n\n"
        f"I am writing to express my strong enthusiasm for the {req.job_title} position. "
        f"As an undergraduate with verified competencies in {skills_str}, I have designed and delivered production-ready systems, "
        f"most notably '{req.highlighted_project}', where I engineered end-to-end scalable architectures and automated testing pipelines.\n\n"
        f"My academic foundation and hands-on experience in building secure, resilient full-stack applications make me confident in my ability "
        f"to make immediate, high-impact contributions to {req.company_name}.\n\n"
        f"Thank you for your time and consideration. I look forward to discussing how my skills align with your engineering goals.\n\n"
        f"Sincerely,\nApplicant"
    )
    return CoverLetterResponse(
        subject=f"Application for {req.job_title} - {req.company_name}",
        cover_letter_body=body
    )

@router.post("/project-mentor", response_model=ProjectMentorResponse)
def project_mentor(req: ProjectMentorRequest):
    idea = req.project_idea
    clean_title = idea.title()
    return ProjectMentorResponse(
        problem_statement=f"Addressing operational inefficiencies, manual data bottlenecks, and security vulnerabilities through '{clean_title}' using decoupled microservices and intelligent automation.",
        objectives=[
            f"Design and implement responsive client interface for {clean_title}",
            "Build secure, RESTful backend microservices with JWT & RBAC authorization",
            "Incorporate anti-proxy / integrity verification and anomaly detection",
            "Integrate automated testing suite and CI/CD container deployment"
        ],
        functional_requirements=[
            "Role-Based Access Control (Student, Faculty, Admin)",
            "Dynamic session token verification with short-lived TOTP intervals",
            "Real-time analytics visualization and audit event stream logging",
            "Interactive AI assistant with grounded RAG knowledge search"
        ],
        non_functional_requirements=[
            "Security: BCrypt password hashing, JWT rotation, and OWASP top 10 hardening",
            "Performance: Sub-150ms 95th percentile API response latency",
            "Reliability: 99.9% uptime with automated error boundary recovery",
            "Usability: Fully responsive layout complying with WCAG 2.1 accessibility standards"
        ],
        architecture_overview="Decoupled React 19 + TypeScript frontend communicating via OpenAPI REST endpoints with a FastAPI Python backend, backed by PostgreSQL relational persistence and vector store for grounded RAG intelligence.",
        database_schema_blueprint=[
            "users (id, email, hashed_password, full_name, role, is_active, created_at)",
            f"{clean_title.lower().replace(' ', '_')}_records (id, entity_id, status, payload_json, timestamp)",
            "audit_logs (id, actor_id, action, resource, details_json, timestamp)",
            "knowledge_documents (id, title, category, content, created_at)"
        ],
        api_endpoints_plan=[
            "POST /api/v1/auth/login -> JWT Access & Refresh tokens",
            f"POST /api/v1/{clean_title.lower().replace(' ', '-')}/execute -> Process core workflow",
            f"GET /api/v1/{clean_title.lower().replace(' ', '-')}/analytics -> Aggregate KPI summary",
            "POST /api/v1/ai/chat -> Permission-aware assistant query"
        ],
        suggested_tech_stack=["React 19", "TypeScript", "FastAPI", "PostgreSQL", "Tailwind CSS", "Docker"],
        milestones=[
            {"phase": "Phase 1: Requirements Specification & Database ER Design", "duration": "Week 1", "status": "COMPLETED"},
            {"phase": "Phase 2: Authentication, Security Middleware & Backend APIs", "duration": "Week 2-3", "status": "IN_PROGRESS"},
            {"phase": "Phase 3: Interactive Frontend Portals & AI Copilot Integration", "duration": "Week 4-5", "status": "PLANNED"},
            {"phase": "Phase 4: Automated Testing, Security Hardening & Dissertation Docs", "duration": "Week 6", "status": "PLANNED"}
        ],
        viva_defense_questions=[
            {
                "question": "How does your architecture prevent unauthorized data access between students?",
                "answer": "All backend endpoints enforce RBAC dependency checks and query filtering strictly scoped to the authenticated user's ID extracted from the validated JWT token."
            },
            {
                "question": "What mechanism is used to eliminate AI hallucinations in university policies?",
                "answer": "Retrieval-Augmented Generation (RAG) retrieves verbatim policy clauses from the verified knowledge base and supplies them as ground truth before generating answers."
            },
            {
                "question": "How does the system handle database concurrency and scaling?",
                "answer": "Relational entities are normalized with foreign key constraints, connection pooling via SQLAlchemy, and Redis caching for high-read session tokens."
            }
        ]
    )
