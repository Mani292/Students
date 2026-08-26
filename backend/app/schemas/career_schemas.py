from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class JobSearchRequest(BaseModel):
    query: Optional[str] = None
    location: Optional[str] = None

class JobMatchRequest(BaseModel):
    job_description: str
    student_skills: List[str]

class JobMatchResponse(BaseModel):
    match_score: float
    matching_skills: List[str]
    missing_skills: List[str]
    recommendations: List[str]

class ResumeAnalysisRequest(BaseModel):
    resume_text: str

class ResumeAnalysisResponse(BaseModel):
    ats_score: float
    extracted_skills: List[str]
    improvement_areas: List[str]

class JobListingOut(BaseModel):
    id: int
    title: str
    company: str
    location: str
    job_type: str = "Internship" # Internship / Full-time
    stipend_or_salary: str = "$3,000 / mo"
    required_skills: List[str]
    description: str

class CoverLetterRequest(BaseModel):
    job_title: str
    company_name: str
    student_skills: List[str]
    highlighted_project: str

class CoverLetterResponse(BaseModel):
    subject: str
    cover_letter_body: str

class ProjectMentorRequest(BaseModel):
    project_idea: str
    domain: Optional[str] = "Full-Stack AI System"

class ProjectMentorResponse(BaseModel):
    problem_statement: str
    objectives: List[str]
    functional_requirements: List[str]
    non_functional_requirements: List[str] = []
    architecture_overview: str
    database_schema_blueprint: List[str] = []
    api_endpoints_plan: List[str] = []
    suggested_tech_stack: List[str]
    milestones: List[Dict[str, Any]]
    viva_defense_questions: List[Dict[str, str]] = []
