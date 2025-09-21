"""
Ocean Chat Backend 2.0 - Configuration Management

Centralized configuration using Pydantic settings with environment variables.
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_RELOAD: bool = True
    DEBUG: bool = True
    
    # Database Configuration
    DATABASE_URL: str = "postgresql://postgres:admin123@localhost:5432/ocean_data"
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 5432
    DATABASE_NAME: str = "ocean_data"
    DATABASE_USER: str = "postgres"
    DATABASE_PASSWORD: str = "admin123"
    
    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # External APIs
    ERDDAP_BASE_URL: str = "https://coastwatch.pfeg.noaa.gov/erddap"
    ARGO_API_KEY: str = "2fc9f5f5d01b045d5aa9c0cfd8da51552b700775"
    NOAA_API_KEY: str = "your_noaa_api_key_here"
    NASA_API_KEY: str = "your_nasa_api_key_here"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Data Source Configuration
    PRIMARY_DATA_SOURCE: str = "api"
    FALLBACK_DATA_SOURCE: str = "database"
    API_TIMEOUT_SECONDS: int = 3
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # CORS Configuration
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001"
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create global settings instance
settings = Settings()