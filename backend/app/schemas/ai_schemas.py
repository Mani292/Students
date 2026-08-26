from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class AIChatRequest(BaseModel):
    message: str

class AIChatResponse(BaseModel):
    response: str
    sources: List[Dict[str, Any]] = []
    tools_used: List[str] = []

class LearningPathRequest(BaseModel):
    subject: str
    career_goal: Optional[str] = "Software Engineer"

class LearningPathResponse(BaseModel):
    subject: str
    roadmap: List[Dict[str, Any]]
    recommended_resources: List[Dict[str, Any]]
