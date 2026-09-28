from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.models.all_models import Department, Faculty, Student, User, UserRole


DEMO_PASSWORD = "password123"


def seed_demo_accounts(db: Session) -> None:
    # Older demo/test databases may contain profiles whose users were removed.
    # Remove only those unusable orphan profiles before creating new accounts.
    users_query = db.query(User.id)
    db.query(Student).filter(~Student.user_id.in_(users_query)).delete(synchronize_session=False)
    db.query(Faculty).filter(~Faculty.user_id.in_(users_query)).delete(synchronize_session=False)
    db.flush()

    department = db.query(Department).filter(Department.code == "CSE").first()
    if not department:
        department = Department(code="CSE", name="Computer Science & Engineering")
        db.add(department)
        db.flush()

    accounts = [
        ("student@univ.edu", "Aarav Student", UserRole.STUDENT),
        ("faculty@univ.edu", "Dr. Priya Faculty", UserRole.FACULTY),
        ("hod@univ.edu", "Dr. Meera HOD", UserRole.HOD),
        ("admin@univ.edu", "University Admin", UserRole.ADMIN),
        ("superadmin@univ.edu", "Platform Super Admin", UserRole.SUPER_ADMIN),
    ]

    for email, full_name, role in accounts:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            user = User(
                email=email,
                hashed_password=get_password_hash(DEMO_PASSWORD),
                full_name=full_name,
                role=role,
                is_active=True,
            )
            db.add(user)
            db.flush()
        elif not verify_password(DEMO_PASSWORD, user.hashed_password):
            user.hashed_password = get_password_hash(DEMO_PASSWORD)

        if role == UserRole.STUDENT and not db.query(Student).filter(Student.user_id == user.id).first():
            db.add(Student(
                user_id=user.id,
                roll_number="DEMO2025001",
                department_id=department.id,
                year=2,
                semester=4,
                cgpa=8.4,
                skills=["Python", "FastAPI", "React"],
                career_interests=["Software Engineering", "AI"],
            ))
        elif role in (UserRole.FACULTY, UserRole.HOD) and not db.query(Faculty).filter(Faculty.user_id == user.id).first():
            db.add(Faculty(
                user_id=user.id,
                employee_id=f"DEMO-{role.value}",
                department_id=department.id,
                designation="Head of Department" if role == UserRole.HOD else "Faculty",
            ))

    # Seed Placement & Career Data
    from app.models.all_models import Company, JobPosting, LearningTrack, LearningResource, AcademicActivity, Topic, Course
    from datetime import datetime, timedelta

    if not db.query(Company).first():
        c1 = Company(name="TechCorp Solutions", website="https://techcorp.com", description="Leading Enterprise Cloud & AI Platform", industry="Software", location="San Francisco, CA")
        c2 = Company(name="DataMind AI Systems", website="https://datamind.ai", description="Advanced Machine Learning & RAG Engine Lab", industry="AI / ML", location="New York, NY")
        db.add_all([c1, c2])
        db.flush()

        jp1 = JobPosting(company_id=c1.id, title="Associate Full-Stack Software Engineer", description="Build web apps with React & Python FastAPI", min_cgpa=7.5, allowed_departments=["CSE", "ECE"], package_ctc="14 LPA", application_deadline=datetime.utcnow() + timedelta(days=30))
        jp2 = JobPosting(company_id=c2.id, title="AI / LLM Systems Engineer", description="Develop RAG pipelines and autonomous tool calling agents", min_cgpa=8.0, allowed_departments=["CSE"], package_ctc="18 LPA", application_deadline=datetime.utcnow() + timedelta(days=45))
        db.add_all([jp1, jp2])

    if not db.query(LearningTrack).first():
        lt1 = LearningTrack(title="Full-Stack Web Engineering", description="Master React, TypeScript, Python FastAPI and cloud deployment", category="Full-Stack", target_role="Software Engineer")
        lt2 = LearningTrack(title="Applied AI & Autonomous Agents", description="Learn LLM orchestration, RAG architectures, and vector search", category="AI / ML", target_role="AI Engineer")
        db.add_all([lt1, lt2])
        db.flush()

        res1 = LearningResource(track_id=lt1.id, title="React 19 & TypeScript State Architecture", resource_type="ARTICLE", url_or_content="https://react.dev", sequence_order=1)
        res2 = LearningResource(track_id=lt1.id, title="Building High-Performance FastAPI Services", resource_type="VIDEO", url_or_content="https://fastapi.tiangolo.com", sequence_order=2)
        db.add_all([res1, res2])

    course = db.query(Course).first()
    if not course:
        course = Course(code="CS201", title="Data Structures & Algorithms", department_id=department.id, credits=4)
        db.add(course)
        db.flush()

    if not db.query(Topic).first():
        t1 = Topic(course_id=course.id, unit_number=1, title="Unit 1: Arrays & Linked Lists", description="Memory management and complexity analysis", status="COMPLETED")
        t2 = Topic(course_id=course.id, unit_number=2, title="Unit 2: Trees & Graph Algorithms", description="DFS, BFS, Dijkstra, and Binary Search Trees", status="IN_PROGRESS")
        db.add_all([t1, t2])

    if not db.query(AcademicActivity).first():
        act = AcademicActivity(title="Mid-Term Capstone Project Submission", description="Submit project SRS and GitHub repo link before Friday", faculty_id=1, activity_type="TASK")
        db.add(act)

    db.commit()
