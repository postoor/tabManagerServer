from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.database import init_db
from app.routers import auth, bookmarks, sync


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="Tab Manager API",
    description="Cross-device tab/bookmark manager with Toby-compatible sync",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(bookmarks.router, prefix="/api")
app.include_router(sync.router, prefix="/api")


@app.get("/", tags=["health"])
async def health_check():
    return {"status": "ok", "service": "Tab Manager API", "version": "1.0.0"}


@app.get("/api/health", tags=["health"])
async def api_health():
    return {"status": "ok"}
