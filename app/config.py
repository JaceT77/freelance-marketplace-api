from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
import os

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

DEFAULT_DATABASE_URL = (
    "postgresql+psycopg:///freelance_marketplace"
)


@dataclass(frozen=True)
class Settings:
    app_name: str
    app_version: str
    api_prefix: str
    docs_url: str
    redoc_url: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    database_url: str


@lru_cache
def get_settings() -> Settings:
    return Settings(
        app_name=os.getenv("APP_NAME", "Freelance Marketplace API"),
        app_version=os.getenv("APP_VERSION", "1.0.0"),
        api_prefix=os.getenv("API_PREFIX", "/api"),
        docs_url=os.getenv("DOCS_URL", "/docs"),
        redoc_url=os.getenv("REDOC_URL", "/redoc"),
        secret_key=os.getenv(
            "SECRET_KEY",
            "change-this-secret-key-to-at-least-32-bytes",
        ),
        algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
        access_token_expire_minutes=int(
            os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
        ),
        database_url=os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL),
    )
