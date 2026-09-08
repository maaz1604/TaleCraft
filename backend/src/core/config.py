from typing import Annotated, List
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict
from pydantic import field_validator

class Settings(BaseSettings):
    API_PREFIX : str = "/api"
    DEBUG:bool = False
    DATABASE_URL:str
    ALLOWED_ORIGINS: Annotated[List[str], NoDecode] = []
    OPENAI_API_KEY:str
    
    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_allowed_origins(cls, value: str | List[str]) -> List[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )
        
settings = Settings()  # type: ignore[call-arg]