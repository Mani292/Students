import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.db.session import Base, engine, SessionLocal
from app.services.rag_engine import seed_knowledge_base, search_knowledge_base

def test_rag_engine():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    seed_knowledge_base(db)

    results = search_knowledge_base("What is the attendance requirement?", db)
    assert len(results) >= 1
    assert "75% attendance" in results[0]["content"]

    results_lib = search_knowledge_base("borrow books library rules", db)
    assert len(results_lib) >= 1
    assert "borrow up to 4 books" in results_lib[0]["content"]

    print("University RAG Pipeline & Knowledge Engine test PASSED.")

if __name__ == "__main__":
    test_rag_engine()
