from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.all_models import KnowledgeDocument

DEFAULT_KNOWLEDGE_BASE = [
    {
        "title": "University Attendance Policy",
        "category": "REGULATIONS",
        "content": "Students are required to maintain a minimum of 75% attendance in each course to be eligible for end-semester examinations. Medical leave up to 10% can be approved by the HOD."
    },
    {
        "title": "Digital ID Card Issuance Procedure",
        "category": "SERVICES",
        "content": "Digital ID cards are accessible via the Smart Student Portal under Digital ID menu. In case of lost physical ID, submit a service request for ID Card replacement."
    },
    {
        "title": "Permission and Leave Rules",
        "category": "REGULATIONS",
        "content": "All leave requests must be submitted online at least 24 hours prior via the Permission Portal. Requests undergo Faculty review followed by HOD approval."
    },
    {
        "title": "Library Book Borrowing Rules",
        "category": "LIBRARY",
        "content": "Undergraduate students can borrow up to 4 books for a duration of 14 days. Overdue books incur a fine of $0.50 per day."
    },
    {
        "title": "Academic Grading & CGPA Calculation",
        "category": "ACADEMIC",
        "content": "University uses a 10-point scale. Grade S (90-100%, 10 pts), Grade A (80-89%, 9 pts), Grade B (70-79%, 8 pts), Grade C (60-69%, 7 pts), Grade D (50-59%, 6 pts). Minimum passing grade is 50%."
    },
    {
        "title": "Hostel Residence & Curfew Guidelines",
        "category": "HOSTEL",
        "content": "Hostel campus curfew is 9:30 PM on weekdays and 10:30 PM on weekends. Night outs require explicit parent approval and warden permission via the portal."
    },
    {
        "title": "Campus Transport & Bus Pass Regulations",
        "category": "TRANSPORT",
        "content": "University buses operate across 12 city routes from 7:00 AM to 6:30 PM. Digital bus passes are valid for the full semester and verifiable via QR scan."
    },
    {
        "title": "Career Placements & Internship Eligibility",
        "category": "CAREER",
        "content": "Students with CGPA >= 6.5 and zero active backlogs are eligible for campus placement drives. Minimum 75% attendance in training sessions is required."
    }
]

def seed_knowledge_base(db: Session):
    existing = db.query(KnowledgeDocument).first()
    if not existing:
        for item in DEFAULT_KNOWLEDGE_BASE:
            doc = KnowledgeDocument(
                title=item["title"],
                category=item["category"],
                content=item["content"]
            )
            db.add(doc)
        db.commit()

def search_knowledge_base(query: str, db: Session, top_k: int = 3) -> List[Dict[str, Any]]:
    seed_knowledge_base(db)
    docs = db.query(KnowledgeDocument).all()
    query_terms = query.lower().split()

    scored_docs = []
    for d in docs:
        score = 0
        text = (d.title + " " + d.content + " " + d.category).lower()
        for term in query_terms:
            if term in text:
                score += 1
        if score > 0:
            scored_docs.append({
                "id": d.id,
                "title": d.title,
                "category": d.category,
                "content": d.content,
                "score": score
            })

    scored_docs.sort(key=lambda x: x["score"], reverse=True)
    return scored_docs[:top_k]
