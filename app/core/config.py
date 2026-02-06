import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_FLASH_MODEL: str = "gemini-3-flash-preview" # User requested
    GEMINI_PRO_MODEL: str = "gemini-3-pro-preview"     # User requested
    
    class Config:
        env_file = ".env"

settings = Settings()
