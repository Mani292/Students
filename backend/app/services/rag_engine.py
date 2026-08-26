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
