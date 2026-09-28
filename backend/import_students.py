import sys
import os
import csv
import json

# Ensure backend path is in Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.session import SessionLocal, Base, engine
from app.models.all_models import User, Student, Department, UserRole
from app.core.security import get_password_hash

def import_students_from_csv(csv_filepath: str):
    """
    Imports student records from a CSV file into the database.
    Supported headers:
    Roll.No, Student Name, Branch, Semester, Gender, Mobile.No, Whatsapp.No, E-mail, Password
    """
    if not os.path.exists(csv_filepath):
        print(f"Error: CSV file '{csv_filepath}' not found.")
        return

    # Ensure all DB tables exist
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        with open(csv_filepath, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            imported_count = 0
            skipped_count = 0

            for row in reader:
                # Normalize column headers (strip whitespace and handle case)
                normalized_row = {k.strip(): v.strip() for k, v in row.items() if k}

                email = normalized_row.get("E-mail") or normalized_row.get("email") or normalized_row.get("Email")
                full_name = normalized_row.get("Student Name") or normalized_row.get("full_name") or normalized_row.get("Name")
                roll_number = normalized_row.get("Roll.No") or normalized_row.get("roll_number") or normalized_row.get("Roll No")
                branch_code = normalized_row.get("Branch") or normalized_row.get("department_code") or "CSE"
                raw_semester = normalized_row.get("Semester") or normalized_row.get("semester") or "1"
                gender = normalized_row.get("Gender") or normalized_row.get("gender")
                mobile_number = normalized_row.get("Mobile.No") or normalized_row.get("mobile_number")
                whatsapp_number = normalized_row.get("Whatsapp.No") or normalized_row.get("whatsapp_number")
                raw_password = normalized_row.get("Password") or normalized_row.get("password") or "Student@123"

                if not email or not full_name or not roll_number:
                    print(f"Skipping row missing essential fields: {row}")
                    skipped_count += 1
                    continue

                # Check if user already exists
                existing_user = db.query(User).filter(User.email == email).first()
                if existing_user:
                    print(f"Skipping existing user: {email}")
                    skipped_count += 1
                    continue

                # Ensure Department exists
                dept = db.query(Department).filter(Department.code == branch_code.upper()).first()
                if not dept:
                    dept = Department(code=branch_code.upper(), name=f"{branch_code.upper()} Department")
                    db.add(dept)
                    db.flush()

                # Parse semester & year
                try:
                    semester = int(raw_semester)
                except ValueError:
                    semester = 1
                year = max(1, (semester + 1) // 2)

                # Create User record
                user = User(
                    email=email,
                    hashed_password=get_password_hash(raw_password),
                    full_name=full_name,
                    role=UserRole.STUDENT,
                    is_active=True
                )
                db.add(user)
                db.flush()

                # Create Student Profile
                student = Student(
                    user_id=user.id,
                    roll_number=roll_number,
                    department_id=dept.id,
                    year=year,
                    semester=semester,
                    gender=gender,
                    mobile_number=mobile_number,
                    whatsapp_number=whatsapp_number,
                    cgpa=8.0,
                    skills=["Python", "FastAPI", "Web Development"],
                    career_interests=["Software Engineering"]
                )
                db.add(student)
                imported_count += 1

            db.commit()
            print(f"\nSuccessfully imported {imported_count} student records! ({skipped_count} skipped)")

    except Exception as e:
        db.rollback()
        print(f"Error during import: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    filepath = sys.argv[1] if len(sys.argv) > 1 else "students.csv"
    import_students_from_csv(filepath)
