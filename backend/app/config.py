from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str

    # One school day, so a student signs in once per session.
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 720

    # Used only by `python -m app.seed`.
    ADMIN_USER: str = "admin"
    ADMIN_PASS: str = ""
    DEFAULT_STAFF_PASSWORD: str = ""
    DEFAULT_STUDENT_PIN: str = ""

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
