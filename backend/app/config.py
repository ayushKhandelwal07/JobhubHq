import os
import json
from typing import List, Union
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = Field(default="postgresql://postgres:password@localhost:5432/portia_jobplatform")
    
    # Portia AI Configuration - REQUIRED
    PORTIA_API_KEY: str = Field(default="", description="Portia Cloud API Key - Get from https://app.portialabs.ai/dashboard")
    
    # LLM Configuration - Google Gemini as Primary
    GOOGLE_GEMINI_API_KEY: str = Field(default="", description="Google Gemini API Key - PRIMARY LLM for Portia")
    GOOGLE_API_KEY: str = Field(default="", description="Google AI API Key - Alternative to Gemini")
    
    # Alternative LLM providers (fallback options)
    OPENAI_API_KEY: str = Field(default="", description="OpenAI API Key - Alternative LLM")
    ANTHROPIC_API_KEY: str = Field(default="", description="Anthropic API Key - Alternative LLM")
    MISTRAL_API_KEY: str = Field(default="", description="Mistral API Key - Alternative LLM")
    
    # External APIs for Portia Tools
    LINKEDIN_CLIENT_ID: str = Field(default="")
    LINKEDIN_CLIENT_SECRET: str = Field(default="")
    GITHUB_TOKEN: str = Field(default="", description="GitHub Personal Access Token for Portia GitHub tool")
    
    # Google Services for Portia Tools
    GOOGLE_CREDENTIALS_PATH: str = Field(default="credentials.json")
    GOOGLE_SHEETS_ID: str = Field(default="")
    
    # Email Configuration for Portia Gmail tool
    SMTP_HOST: str = Field(default="smtp.gmail.com")
    SMTP_PORT: int = Field(default=587)
    SMTP_USER: str = Field(default="")
    SMTP_PASSWORD: str = Field(default="")
    
    # Browser Automation for Portia
    BROWSERBASE_API_KEY: str = Field(default="", description="Browserbase API Key for remote browser automation")
    BROWSERBASE_PROJECT_ID: str = Field(default="", description="Browserbase Project ID")
    
    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379")
    
    # JWT Configuration
    JWT_SECRET_KEY: str = Field(default="your-secret-key-change-in-production")
    JWT_ALGORITHM: str = Field(default="HS256")
    JWT_EXPIRATION_HOURS: int = Field(default=24)
    
    # Application Settings
    ENVIRONMENT: str = Field(default="development")
    DEBUG: bool = Field(default=True)
    CORS_ORIGINS: Union[str, List[str]] = Field(default="http://localhost:3000,http://localhost:5173,http://localhost:8080", description="CORS origins as comma-separated list")
    
    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v
    
    # File Upload
    MAX_FILE_SIZE: int = Field(default=10485760)  # 10MB
    UPLOAD_DIR: str = Field(default="uploads")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        env_ignore_empty = True
        env_ignore_empty = True

# Global settings instance
settings = Settings()
