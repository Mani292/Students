import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.db.session import Base, engine, SessionLocal
from app.models.all_models import User, UserRole, Student, Department
from app.core.security import get_password_hash, create_access_token
from app.api.v1.ai import router as ai_router

app = FastAPI()
app.include_router(ai_router, prefix="/api/v1")

def test_ai_api():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    dept = db.query(Department).filter(Department.code == "AI_DEPT").first()
    if not dept:
        dept = Department(code="AI_DEPT", name="Artificial Intelligence")
        db.add(dept)
        db.commit()

    user = db.query(User).filter(User.email == "ai_student@univ.edu").first()
    if not user:
        user = User(email="ai_student@univ.edu", hashed_password=get_password_hash("p"), full_name="Eve AI", role=UserRole.STUDENT)
        db.add(user)
        db.commit()

        student = Student(user_id=user.id, roll_number="AI001", department_id=dept.id, cgpa=3.9, skills=["Python", "TensorFlow"])
        db.add(student)
        db.commit()

    client = TestClient(app)
    token = create_access_token(subject=user.id, role="STUDENT")

    # 1. AI Copilot Chat query on profile
    res = client.post("/api/v1/ai/chat", json={"message": "Show my student profile and cgpa"}, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200, res.text
    chat_resp = res.json()
    assert "AI001" in chat_resp["response"]
    assert "get_student_profile_tool" in chat_resp["tools_used"]

    # 2. AI Copilot Chat query on attendance rules (RAG)
    res = client.post("/api/v1/ai/chat", json={"message": "What is the attendance policy requirement?"}, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200, res.text
    chat_resp = res.json()
    assert "75% attendance" in chat_resp["response"]
    assert "search_university_knowledge_tool" in chat_resp["tools_used"]

    # 3. Learning Path Generator
    res = client.post("/api/v1/ai/learning-path", json={"subject": "Machine Learning", "career_goal": "AI Research Engineer"}, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200, res.text
    lp = res.json()
    assert lp["subject"] == "Machine Learning"
    assert len(lp["roadmap"]) == 4

    print("AI University Copilot & Learning Hub API test PASSED.")

if __name__ == "__main__":
    test_ai_api()
