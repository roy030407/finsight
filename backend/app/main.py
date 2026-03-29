from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import logging

from app.core.config import settings
from app.database.database import create_tables
from app.models import *  # must be before create_tables()
from app.routers import auth, category, transactions, analytics, goals, investments, chat, export

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Safe startup - initialize database with error handling
logger.info("🔄 Starting FinSight API...")
try:
    db_success = create_tables()
    if db_success:
        logger.info("✅ Database initialized successfully")
    else:
        logger.warning("⚠️ Database initialization failed, but continuing startup")
except Exception as e:
    logger.error(f"❌ Database startup error: {e}")
    logger.warning("⚠️ Application will start but database features may be limited")

app = FastAPI(
    title="FinSight API",
    description="AI-powered personal finance platform by Roy Harwani",
    version="1.0.0",
    debug=settings.debug,
)

# ── CORS ─────────────────────────────────────────────────────────
# Reads ALLOWED_ORIGINS env var set by render.yaml
# Falls back to localhost for local development
allowed_origins_raw = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://localhost:5174"
)

allowed_origins = [o.strip() for o in allowed_origins_raw.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(auth.router)
app.include_router(category.router)
app.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
app.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
app.include_router(goals.router)
app.include_router(investments.router)
app.include_router(chat.router, prefix="/chat", tags=["ai-chat"])
app.include_router(export.router, prefix="/export", tags=["export"])

@app.get("/health")
async def health_check():
    """Health check endpoint — must stay lightweight for Render pings"""
    from app.database.database import AsyncSessionLocal

    services = {}

    # Database check
    try:
        services["database"] = "ok" if AsyncSessionLocal else "unavailable"
    except Exception:
        services["database"] = "unavailable"

    # RAG pipeline check
    try:
        from rag.pipeline import rag_pipeline
        services["ai_chat"] = "ok" if rag_pipeline else "unavailable"
    except Exception:
        services["ai_chat"] = "unavailable"

    # ML classifier check
    try:
        from ml.classifier import classifier
        services["ml_classifier"] = "ok" if (classifier and classifier.is_trained) else "unavailable"
    except Exception:
        services["ml_classifier"] = "unavailable"

    overall = "degraded" if any(v == "unavailable" for v in services.values()) else "ok"

    return {
        "status": overall,
        "app": "FinSight",
        "version": "1.0.0",
        "services": services,
    }