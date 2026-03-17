from collections.abc import AsyncGenerator
from pathlib import Path
from typing import Any

from sqlalchemy import event
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings


class Base(DeclarativeBase):
    pass


def _is_sqlite_url(database_url: str) -> bool:
    return make_url(database_url).drivername.startswith("sqlite")


def create_engine_from_url(database_url: str, **kwargs: Any) -> AsyncEngine:
    if _is_sqlite_url(database_url):
        database_path = make_url(database_url).database
        if database_path and database_path != ":memory:":
            Path(database_path).expanduser().parent.mkdir(parents=True, exist_ok=True)
        connect_args = {"check_same_thread": False, **kwargs.pop("connect_args", {})}
        engine = create_async_engine(
            database_url,
            pool_pre_ping=True,
            connect_args=connect_args,
            **kwargs,
        )

        @event.listens_for(engine.sync_engine, "connect")
        def _set_sqlite_pragma(dbapi_connection, _) -> None:
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

        return engine

    return create_async_engine(database_url, pool_pre_ping=True, **kwargs)


settings = get_settings()
engine = create_engine_from_url(settings.database_url)
SessionLocal = async_sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as db:
        yield db


async def init_db() -> None:
    import app.models

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)


async def dispose_db() -> None:
    await engine.dispose()
