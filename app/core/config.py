import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_PRO_MODEL: str = "gemini-3-pro-preview"     
    
    class Config:
        env_file = ".env"

settings = Settings()
