"""
Configuration management for the Job Interview AI Agent.
"""
from typing import List, Optional
from pydantic import BaseModel
from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

load_dotenv(override=True)

class LLMConfig(BaseModel):
    """Configuration for a Language Model service."""
    api_key: str
    model_name: str
    base_url: str | None = None

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    GRADIO_PORT: int = 7860
    NAME: str = "AI Interview Agent"
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    DEEPSEEK_API_KEY: str | None = None
    ANTHROPIC_API_KEY: str | None = None
    GROQ_API_KEY: str | None = None
    LOCAL_DATA: str | None = None
    PROD_TARGET: str | None = None
    
    # LLM configurations
    answer_generator: LLMConfig = LLMConfig(
        api_key=os.getenv("OPENAI_API_KEY", ""),
        model_name="gpt-4o-mini",
        base_url=None
    )
    
    answer_evaluator: LLMConfig = LLMConfig(
        api_key=os.getenv("GOOGLE_API_KEY", ""),
        model_name="gemini-2.0-flash",
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )
    
    # Supported languages
    supported_languages: List[str] = ["German", "English", "French", "Dutch", "Spanish"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create global settings instance
settings = Settings() 