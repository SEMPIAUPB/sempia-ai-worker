import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL_ID: str = os.getenv("GEMINI_MODEL_ID", "gemini-1.5-flash-8b")
    DKT_MODEL_VERSION: str = os.getenv("DKT_MODEL_VERSION", "v1.0")
    
    class Config:
        env_file = ".env"

settings = Settings()
