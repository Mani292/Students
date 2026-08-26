from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.models.all_models import Department, Course, ClassSession, Enrollment, UserRole, User
from app.schemas.schemas import DepartmentCreate, DepartmentOut, CourseCreate, CourseOut, ClassSessionCreate, ClassSessionOut
from app.core.rbac import require_roles, get_current_user

router = APIRouter(prefix="/academic", tags=["Academic & Rosters"])

@router.post("/departments", response_model=DepartmentOut)
def create_department(
    dept_in: DepartmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.SUPER_ADMIN]))
):
    existing = db.query(Department).filter(Department.code == dept_in.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Department code already exists")
    dept = Department(code=dept_in.code, name=dept_in.name)
    db.add(dept)
    db.commit()
    db.refresh(dept)
    return dept

@router.get("/departments", response_model=List[DepartmentOut])
def list_departments(db: Session = Depends(get_db)):
    return db.query(Department).all()

@router.post("/courses", response_model=CourseOut)
def create_course(
    course_in: CourseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.SUPER_ADMIN, UserRole.HOD]))
):
    course = Course(
        code=course_in.code,
        title=course_in.title,
        department_id=course_in.department_id,
        credits=course_in.credits
    )
    db.add(course)
    db.commit()
    db.refresh(course)
    return course

@router.get("/courses", response_model=List[CourseOut])
def list_courses(db: Session = Depends(get_db)):
    return db.query(Course).all()

@router.post("/classes", response_model=ClassSessionOut)
def create_class_session(
    class_in: ClassSessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.SUPER_ADMIN, UserRole.HOD]))
):
    class_obj = ClassSession(
        course_id=class_in.course_id,
        faculty_id=class_in.faculty_id,
        academic_year=class_in.academic_year,
        semester=class_in.semester,
        room_number=class_in.room_number
    )
    db.add(class_obj)
    db.commit()
    db.refresh(class_obj)
    return class_obj

@router.get("/classes", response_model=List[ClassSessionOut])
def list_classes(db: Session = Depends(get_db)):
    return db.query(ClassSession).all()
