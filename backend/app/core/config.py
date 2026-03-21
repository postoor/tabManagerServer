from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List
import json


class Settings(BaseSettings):
    SECRET_KEY: str = "changeme-in-production-use-a-long-random-string"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days

    DATABASE_URL: str = "sqlite+aiosqlite:///./tabmanager.db"

    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except Exception:
                return [origin.strip() for origin in v.split(",")]
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
