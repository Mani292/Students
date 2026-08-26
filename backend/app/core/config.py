import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI-Powered Smart University Ecosystem"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("JWT_SECRET", os.getenv("SECRET_KEY", "super-secret-key-smart-university-2025"))
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 # 1 day for dev simplicity
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days

    AI_PROVIDER: str = "local"
    AI_MODEL: str = "glm-4.7"
    AI_API_KEY: str = ""
    AI_BASE_URL: str = ""
    AI_TIMEOUT_SECONDS: int = 20
    CORS_ORIGINS: str = "http://localhost:3000"

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./smart_university.db")

    class Config:
        case_sensitive = True

settings = Settings()
