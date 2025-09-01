"""
Configuration management for OpenFiles Python SDK
"""

from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """OpenFiles SDK Configuration Settings"""
    
    # OpenAPI URL for fetching latest spec
    openfiles_openapi_url: Optional[str] = Field(
        default=None,
        description="URL to fetch OpenAPI specification from live API"
    )
    
    # Debug mode
    debug: bool = Field(
        default=False,
        description="Enable debug logging"
    )
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    @field_validator("openfiles_openapi_url")
    @classmethod
    def validate_openapi_url(cls, v: Optional[str]) -> Optional[str]:
        """Validate OpenAPI URL format"""
        if v is None:
            return v
        
        if not v.startswith(("http://", "https://")):
            raise ValueError("OpenAPI URL must start with http:// or https://")
        
        return v


# Global settings instance
settings = Settings()