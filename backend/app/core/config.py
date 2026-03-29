from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    database_url: str

    # Auth
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # AI
    gemini_api_key: str = ""

    # App
    environment: str = "development"
    allowed_origins: str = "http://localhost:5173,http://localhost:5174"

    # Debug is False in production
    @property
    def debug(self) -> bool:
        return self.environment != "production"

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()