from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import timedelta

from app.db.session import get_db
from app.models.all_models import Department, Student, User, UserRole
from app.core.rbac import get_current_user
from app.core.security import verify_password, create_access_token, create_refresh_token, decode_token, get_password_hash
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication Service"])

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    role: str
    email: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str


class StudentRegistrationRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=2, max_length=120)
    roll_number: str = Field(min_length=3, max_length=40)
    department_code: str = Field(default="CSE", min_length=2, max_length=20)

@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not user.is_active or not verify_password(req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    access_token = create_access_token(subject=user.id, role=user.role.value)
    refresh_token = create_refresh_token(subject=user.id, role=user.role.value)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        role=user.role.value,
        email=user.email
    )


@router.post("/register", response_model=TokenResponse, status_code=201)
def register_student(req: StudentRegistrationRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == req.email).first():
        raise HTTPException(status_code=409, detail="Email is already registered")
    if db.query(Student).filter(Student.roll_number == req.roll_number).first():
        raise HTTPException(status_code=409, detail="Roll number is already registered")

    department = db.query(Department).filter(Department.code == req.department_code.upper()).first()
    if not department:
        raise HTTPException(status_code=400, detail="Department code not found")

    user = User(
        email=req.email,
        hashed_password=get_password_hash(req.password),
        full_name=req.full_name.strip(),
        role=UserRole.STUDENT,
        is_active=True,
    )
    try:
        db.add(user)
        db.flush()
        db.add(Student(
            user_id=user.id,
            roll_number=req.roll_number.strip(),
            department_id=department.id,
            year=1,
            semester=1,
            skills=[],
            career_interests=[],
        ))
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(status_code=409, detail="Email or roll number is already registered") from error

    return TokenResponse(
        access_token=create_access_token(subject=user.id, role=user.role.value),
        refresh_token=create_refresh_token(subject=user.id, role=user.role.value),
        role=user.role.value,
        email=user.email,
    )

@router.post("/refresh", response_model=TokenResponse)
def refresh_token(req: RefreshTokenRequest, db: Session = Depends(get_db)):
    payload = decode_token(req.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )

    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    new_access_token = create_access_token(subject=user.id, role=user.role.value)
    new_refresh_token = create_refresh_token(subject=user.id, role=user.role.value)

    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        role=user.role.value,
        email=user.email
    )


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role.value,
        "is_active": current_user.is_active,
    }
