import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.career import router as career_router

app = FastAPI()
app.include_router(career_router, prefix="/api/v1")

def test_career_api():
    client = TestClient(app)

    # 1. Get jobs
    res = client.get("/api/v1/career-project/jobs")
    assert res.status_code == 200
    assert len(res.json()) >= 1

    # 2. Match job
    res = client.post("/api/v1/career-project/match-job", json={
        "job_description": "We need a Full-Stack Engineer skilled in Python, FastAPI, React, and Docker.",
        "student_skills": ["Python", "FastAPI"]
    })
    assert res.status_code == 200, res.text
    match_data = res.json()
    assert "Python" in match_data["matching_skills"]
    assert "Docker" in match_data["missing_skills"]

    # 3. Analyze resume
    res = client.post("/api/v1/career-project/analyze-resume", json={
        "resume_text": "Experienced student developer working with Python, FastAPI, SQL, and Git."
    })
    assert res.status_code == 200, res.text
    res_data = res.json()
    assert res_data["ats_score"] > 50.0

    # 4. Project Mentor
    res = client.post("/api/v1/career-project/project-mentor", json={
        "project_idea": "AI Powered Traffic Management"
    })
    assert res.status_code == 200, res.text
    mentor_data = res.json()
    assert len(mentor_data["milestones"]) == 4

    print("AI Career Engine & Project Lab Workspace API test PASSED.")

if __name__ == "__main__":
    test_career_api()
