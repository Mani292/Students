from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from datetime import timedelta

from app.db.session import get_db
from app.models.all_models import User
from app.core.security import verify_password, create_access_token, create_refresh_token, decode_token
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

@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not verify_password(req.password, user.hashed_password):
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
    if not user:
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
