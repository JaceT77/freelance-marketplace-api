from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import auth, bids, contracts, projects, reviews
from app.config import get_settings
from app.database import dispose_db, init_db


settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    await init_db()
    yield
    await dispose_db()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="API for a freelance marketplace where clients hire freelancers.",
    docs_url=settings.docs_url,
    redoc_url=settings.redoc_url,
    lifespan=lifespan,
)

app.include_router(auth.router, prefix=settings.api_prefix)
app.include_router(projects.router, prefix=settings.api_prefix)
app.include_router(bids.router, prefix=settings.api_prefix)
app.include_router(contracts.router, prefix=settings.api_prefix)
app.include_router(reviews.router, prefix=settings.api_prefix)


@app.get("/", tags=["Health"])
async def root():
    return {
        "message": "Freelance Marketplace API is running.",
        "docs": settings.docs_url,
        "redoc": settings.redoc_url,
    }


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}
