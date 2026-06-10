from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import settings
from app.config.database import engine, Base

from app.api.v1 import (
    auth,
    battles,
    images,
    chat
)

# إنشاء الجداول
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(
    auth.router,
    prefix="/api/v1/auth",
    tags=["Authentication"]
)

app.include_router(
    battles.router,
    prefix="/api/v1/battles",
    tags=["Battles"]
)

app.include_router(
    images.router,
    prefix="/api/v1/images",
    tags=["Images"]
)

app.include_router(
    chat.router,
    prefix="/api/v1/chat",
    tags=["Chat"]
)


@app.get("/")
def root():
    return {
        "message": "AI Arena Enterprise API is running 🚀"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "version": "2.0.0"
    }
