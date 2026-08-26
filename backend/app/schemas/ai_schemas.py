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

class AIConceptExplainRequest(BaseModel):
    concept: str
    depth: Optional[str] = "INTERMEDIATE" # "BEGINNER", "INTERMEDIATE", "ADVANCED"

class AIConceptExplainResponse(BaseModel):
    concept: str
    explanation: str
    key_points: List[str]
    code_example: Optional[str] = None
    practice_question: str

class AIQuizRequest(BaseModel):
    topic: str
    num_questions: int = 4

class QuizQuestion(BaseModel):
    id: int
    question: str
    options: List[str]
    correct_option_index: int
    explanation: str

class AIQuizResponse(BaseModel):
    topic: str
    questions: List[QuizQuestion]

class AIFlashcard(BaseModel):
    id: int
    front: str
    back: str
    category: str

class AIFlashcardsResponse(BaseModel):
    topic: str
    cards: List[AIFlashcard]

class RAGDocCreate(BaseModel):
    title: str
    category: str
    content: str
    source: Optional[str] = "University Manual"

class RAGDocOut(BaseModel):
    id: int
    title: str
    category: str
    content: str
    source: Optional[str] = None

    class Config:
        from_attributes = True
