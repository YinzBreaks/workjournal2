from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str

    ENTRA_TENANT_ID: str
    ENTRA_CLIENT_ID: str
    ENTRA_CLIENT_SECRET: str
    ENTRA_REDIRECT_URI: str

    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    DEFAULT_STUDENT_PIN: str = ""
    ADMIN_USER: str = "admin"
    ADMIN_PASS: str = ""

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
