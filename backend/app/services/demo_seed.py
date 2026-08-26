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

    db.commit()
