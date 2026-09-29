from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.all_models import User, Student
from app.schemas.career_schemas import (
    JobSearchRequest, JobMatchRequest, JobMatchResponse, ResumeAnalysisRequest, ResumeAnalysisResponse,
    ProjectMentorRequest, ProjectMentorResponse
)
from app.core.rbac import get_current_user, require_roles
from app.models.all_models import UserRole

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
def get_jobs(db: Session = Depends(get_db)):
    from app.models.all_models import JobPosting, Company
    postings = db.query(JobPosting).all()
    if postings:
        result = []
        for p in postings:
            c = db.query(Company).filter(Company.id == p.company_id).first()
            result.append({
                "id": p.id,
                "title": p.title,
                "company": c.name if c else "Company",
                "package_ctc": p.package_ctc,
                "location": c.location if c else "Campus",
                "min_cgpa": p.min_cgpa,
                "description": p.description,
                "required_skills": p.allowed_departments or ["Engineering"]
            })
        return result
    return MOCK_JOBS

@router.get("/companies")
def list_companies(db: Session = Depends(get_db)):
    from app.models.all_models import Company
    return db.query(Company).all()

@router.post("/companies")
def create_company(
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.SUPER_ADMIN]))
):
    from app.models.all_models import Company
    comp = Company(
        name=payload.get("name"),
        website=payload.get("website"),
        description=payload.get("description"),
        industry=payload.get("industry"),
        location=payload.get("location")
    )
    db.add(comp)
    db.commit()
    db.refresh(comp)
    return comp

@router.post("/postings")
def create_job_posting(
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.SUPER_ADMIN]))
):
    from app.models.all_models import JobPosting
    from datetime import datetime
    posting = JobPosting(
        company_id=payload.get("company_id", 1),
        title=payload.get("title", "Software Engineer"),
        description=payload.get("description", "Exciting tech role"),
        min_cgpa=payload.get("min_cgpa", 6.5),
        allowed_departments=payload.get("allowed_departments", ["CSE", "ECE"]),
        package_ctc=payload.get("package_ctc", "10 LPA"),
        application_deadline=datetime.utcnow()
    )
    db.add(posting)
    db.commit()
    db.refresh(posting)
    return posting

@router.get("/applications")
def list_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from app.models.all_models import JobApplication, Student, JobPosting, Company
    query = db.query(JobApplication)
    if current_user.role == UserRole.STUDENT:
        student = db.query(Student).filter(Student.user_id == current_user.id).first()
        if student:
            query = query.filter(JobApplication.student_id == student.id)
        else:
            return []
    apps = query.all()
    res = []
    for a in apps:
        jp = db.query(JobPosting).filter(JobPosting.id == a.job_id).first()
        comp = db.query(Company).filter(Company.id == jp.company_id).first() if jp else None
        res.append({
            "id": a.id,
            "job_title": jp.title if jp else "Role",
            "company_name": comp.name if comp else "Tech Corp",
            "status": a.status.value if hasattr(a.status, 'value') else str(a.status),
            "applied_at": a.applied_at
        })
    return res

@router.post("/apply/{job_id}")
def apply_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.STUDENT]))
):
    from app.models.all_models import JobApplication, Student, JobApplicationStatus
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile missing")
    existing = db.query(JobApplication).filter(JobApplication.job_id == job_id, JobApplication.student_id == student.id).first()
    if existing:
        return {"message": "Already applied", "application_id": existing.id}
    app_obj = JobApplication(
        job_id=job_id,
        student_id=student.id,
        status=JobApplicationStatus.APPLIED
    )
    db.add(app_obj)
    db.commit()
    db.refresh(app_obj)
    return {"message": "Application submitted successfully", "application_id": app_obj.id}

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
