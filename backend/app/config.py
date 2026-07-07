import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environmental variables from .env file if it exists
load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "DecisionSphere AI"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Gemini Configuration
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./decisionsphere.db")
    
    # Security Configuration
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-decisionsphere-ai-token-key-2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    
    # Rate Limiting
    RATE_LIMIT_CALLS: int = 100
    RATE_LIMIT_WINDOW_SECONDS: int = 60
    
    class Config:
        case_sensitive = True

settings = Settings()
