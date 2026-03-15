from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
import os

from dotenv import load_dotenv
from sqlalchemy.engine import URL, make_url


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

DEFAULT_DATABASE_DRIVER = "postgresql+asyncpg"
DEFAULT_DATABASE_NAME = "freelance_marketplace"
DEFAULT_TEST_DATABASE_NAME = "freelance_marketplace_test"


def _get_optional_env(name: str, fallback_name: str | None = None) -> str | None:
    value = os.getenv(name)
    if value is None and fallback_name is not None:
        value = os.getenv(fallback_name)
    if value is None:
        return None

    value = value.strip()
    return value or None


def _get_optional_port(name: str, fallback_name: str | None = None) -> int | None:
    value = _get_optional_env(name, fallback_name)
    return int(value) if value else None


def normalize_database_url(database_url: str) -> str:
    url = make_url(database_url)
    if not url.drivername.startswith("postgresql"):
        raise ValueError("Only PostgreSQL database URLs are supported.")
    if url.drivername != DEFAULT_DATABASE_DRIVER:
        url = url.set(drivername=DEFAULT_DATABASE_DRIVER)
    return url.render_as_string(hide_password=False)


def build_database_url(
    *,
    database_name: str,
    host: str | None = None,
    port: int | None = None,
    username: str | None = None,
    password: str | None = None,
    database_url: str | None = None,
) -> str:
    if database_url:
        return normalize_database_url(database_url)

    return URL.create(
        drivername=DEFAULT_DATABASE_DRIVER,
        username=username,
        password=password if username else None,
        host=host,
        port=port if host else None,
        database=database_name,
    ).render_as_string(hide_password=False)


def get_database_url_from_env() -> str:
    return build_database_url(
        database_name=os.getenv("DATABASE_NAME", DEFAULT_DATABASE_NAME),
        host=_get_optional_env("DATABASE_HOST"),
        port=_get_optional_port("DATABASE_PORT"),
        username=_get_optional_env("DATABASE_USER"),
        password=_get_optional_env("DATABASE_PASSWORD"),
        database_url=_get_optional_env("DATABASE_URL"),
    )


def get_test_database_url_from_env() -> str:
    return build_database_url(
        database_name=os.getenv("TEST_DATABASE_NAME", DEFAULT_TEST_DATABASE_NAME),
        host=_get_optional_env("TEST_DATABASE_HOST", "DATABASE_HOST"),
        port=_get_optional_port("TEST_DATABASE_PORT", "DATABASE_PORT"),
        username=_get_optional_env("TEST_DATABASE_USER", "DATABASE_USER"),
        password=_get_optional_env("TEST_DATABASE_PASSWORD", "DATABASE_PASSWORD"),
        database_url=_get_optional_env("TEST_DATABASE_URL"),
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
    test_database_url: str


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
        database_url=get_database_url_from_env(),
        test_database_url=get_test_database_url_from_env(),
    )
