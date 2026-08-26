from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.all_models import User, Student
from app.schemas.career_schemas import (
    JobSearchRequest, JobMatchRequest, JobMatchResponse, ResumeAnalysisRequest, ResumeAnalysisResponse,
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
        "required_skills": ["Python", "React", "FastAPI", "SQL", "Docker"]
    },
    {
        "id": 2,
        "title": "AI / Machine Learning Engineer Associate",
        "company": "DataMind AI Lab",
        "location": "New York, NY",
        "required_skills": ["Python", "TensorFlow", "PyTorch", "RAG", "SQL"]
    }
]

@router.get("/jobs")
def get_jobs():
    return MOCK_JOBS

@router.post("/match-job", response_model=JobMatchResponse)
def match_job(req: JobMatchRequest):
    jd_terms = [t.strip().lower() for t in req.job_description.replace("\n", " ").split() if len(t) > 2]
    user_skills_lower = [s.lower() for s in req.student_skills]

    matching = [s for s in req.student_skills if s.lower() in req.job_description.lower()]
    missing = []

    common_reqs = ["Python", "React", "FastAPI", "Docker", "AWS", "SQL", "Kubernetes", "PyTorch"]
    for r in common_reqs:
        if r.lower() in req.job_description.lower() and r.lower() not in user_skills_lower:
            missing.append(r)

    total_reqs = max(len(matching) + len(missing), 1)
    score = min(round((len(matching) / total_reqs) * 100.0, 1), 100.0)

    recs = []
    if missing:
        recs.append(f"Consider building a hands-on project using {', '.join(missing[:2])} to fill key skill gaps.")
    recs.append("Highlight verifiable university coursework and capstone projects in your resume.")

    return JobMatchResponse(
        match_score=score,
        matching_skills=matching,
        missing_skills=missing,
        recommendations=recs
    )

@router.post("/analyze-resume", response_model=ResumeAnalysisResponse)
def analyze_resume(req: ResumeAnalysisRequest):
    text = req.resume_text
    skills_catalog = ["Python", "React", "FastAPI", "SQL", "Docker", "AWS", "TypeScript", "Git", "Machine Learning", "C++", "Java"]
    found = [s for s in skills_catalog if s.lower() in text.lower()]

    score = min(50.0 + len(found) * 5.0, 95.0)
    improvements = []
    if "docker" not in text.lower():
        improvements.append("Add containerization experience (Docker/Kubernetes).")
    if "metric" not in text.lower() and "improved" not in text.lower():
        improvements.append("Quantify project impacts (e.g., 'Improved API latency by 35%').")

    return ResumeAnalysisResponse(
        ats_score=score,
        extracted_skills=found,
        improvement_areas=improvements
    )

@router.post("/project-mentor", response_model=ProjectMentorResponse)
def project_mentor(req: ProjectMentorRequest):
    idea = req.project_idea
    return ProjectMentorResponse(
        problem_statement=f"Modernizing inefficient workflows through '{idea}' by leveraging scalable software design.",
        objectives=[
            "Design and implement responsive client interface",
            "Build secure, RESTful backend microservices",
            "Integrate automated testing and continuous integration pipeline"
        ],
        functional_requirements=[
            "User Authentication & Role-Based Access Control",
            "Real-time data visualization dashboard",
            "Automated alert notification dispatch"
        ],
        architecture_overview="Decoupled React frontend communicating with FastAPI microservices and PostgreSQL relational storage.",
        suggested_tech_stack=["React", "TypeScript", "FastAPI", "PostgreSQL", "Docker"],
        milestones=[
            {"phase": "Phase 1: SRS & Database Schema", "duration": "1 Week"},
            {"phase": "Phase 2: Backend API & Auth Implementation", "duration": "2 Weeks"},
            {"phase": "Phase 3: Frontend Interface & AI Copilot Integration", "duration": "2 Weeks"},
            {"phase": "Phase 4: Testing & Deployment", "duration": "1 Week"}
        ]
    )
