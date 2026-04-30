from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.routers import upload
from .routers import posts, users, auth
from .config import settings
from .routers import posts, users, auth, websocket
import logging
import os

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)

# uploads papkasi yaratish
os.makedirs("uploads", exist_ok=True)

# Production da docs o'chirish (ixtiyoriy)
app = FastAPI(
    title="Blog API",
    version="5.0.0",
    docs_url=None if settings.is_production else "/docs",
    redoc_url=None if settings.is_production else "/redoc",
    openapi_url=None if settings.is_production else "/openapi.json",
)

# Statik fayllar
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(posts.router)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(websocket.router)
app.include_router(upload.router)

@app.get("/")
def root():
    return {
        "xabar": "Blog API",
        "version": "5.0.0",
        "environment": settings.environment
    }

# Health check — deploy platformalar uchun
@app.get("/health")
def health_check():
    return {"status": "ok"}