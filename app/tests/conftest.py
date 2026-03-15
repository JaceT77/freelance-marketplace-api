from pathlib import Path
import os
import sys

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.orm import sessionmaker

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

DEFAULT_TEST_DATABASE_URL = (
    "postgresql+psycopg:///freelance_marketplace_test"
)
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", DEFAULT_TEST_DATABASE_URL)
os.environ["DATABASE_URL"] = TEST_DATABASE_URL

from app.database import Base, create_engine_from_url, get_db
from app.main import app


engine = create_engine_from_url(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


@pytest.fixture()
async def client():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    async def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as test_client:
        yield test_client
    app.dependency_overrides.clear()
