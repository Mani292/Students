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

class ProjectMentorRequest(BaseModel):
    project_idea: str

class ProjectMentorResponse(BaseModel):
    problem_statement: str
    objectives: List[str]
    functional_requirements: List[str]
    architecture_overview: str
    suggested_tech_stack: List[str]
    milestones: List[Dict[str, Any]]
