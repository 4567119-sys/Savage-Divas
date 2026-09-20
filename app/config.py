import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Royal Square Financial Backend"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./royal_square.db")
    AI_CONFIDENCE_THRESHOLD: float = 0.80

    class Config:
        case_sensitive = True

settings = Settings()
