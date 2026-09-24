from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Required. No fallback: the app refuses to boot without it.
    DATABASE_URL: str

    # The one program this deployment serves (a code from seed_data.PROGRAMS).
    CLASS_PROGRAM_CODE: str = "NETWORK-CYBER"

    # Where "Sign out" sends people: the Authelia portal's logout page.
    AUTHELIA_LOGOUT_URL: str = "https://auth.beattietech.local/logout"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
