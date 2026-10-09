from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.meters import router as meters_router
from app.services.urja_client import UrjaClient


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.urja_client = UrjaClient()
    try:
        yield
    finally:
        await app.state.urja_client.close()


app = FastAPI(
    title="Urja Meter Adapter",
    description="API adapter for the Urja Meter Ops portal.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(meters_router)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/")
async def root():
    return {
        "name": "Urja Meter Adapter",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }

