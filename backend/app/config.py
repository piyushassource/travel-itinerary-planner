import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Personalized Travel Itinerary Planner"
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ]
    
    # LLM Settings
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    DEFAULT_MODEL: str = "gemini-1.5-pro"
    
    # Supabase Settings (Public / Anon Client)
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    
    # Supabase Service Role Key (Admin / Elevated Permissions)
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
