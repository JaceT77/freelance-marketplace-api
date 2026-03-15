import asyncio
from pathlib import Path
import sys

from sqlalchemy import select

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.database import SessionLocal, init_db
from app.models.user import User
from app.schemas.auth import RegisterRequest
from app.services.auth_service import register_user


TEST_USERS = [
    {
        "username": "client1",
        "email": "client1@example.com",
        "password": "client123",
        "role": "client",
        "bio": "Default client account for manual testing.",
    },
    {
        "username": "freelancer1",
        "email": "freelancer1@example.com",
        "password": "freelancer123",
        "role": "freelancer",
        "bio": "Default freelancer account for manual testing.",
    },
]


async def main() -> None:
    await init_db()
    async with SessionLocal() as db:
        for payload in TEST_USERS:
            existing_user = await db.scalar(
                select(User).where(User.username == payload["username"])
            )
            if existing_user:
                print(f"Skipped existing user: {existing_user.username}")
                continue

            user = await register_user(db, RegisterRequest(**payload))
            print(f"Created user: {user.username} ({user.role.value})")


if __name__ == "__main__":
    asyncio.run(main())
