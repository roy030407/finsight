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

# Configure CORS middleware
origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    os.getenv("FRONTEND_URL", "https://finsight-ui.onrender.com"),
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
    """Health check endpoint with service status"""
    from app.database.database import AsyncSessionLocal
    from rag.pipeline import rag_pipeline
    from ml.classifier import classifier
    
    status = {
        "status": "ok",
        "app": "FinSight",
        "version": "1.0.0",
        "services": {
            "database": "ok" if AsyncSessionLocal else "unavailable",
            "ai_chat": "ok" if rag_pipeline else "unavailable", 
            "ml_classifier": "ok" if classifier and classifier.is_trained else "unavailable"
        }
    }
    
    # Determine overall status
    if any(service == "unavailable" for service in status["services"].values()):
        status["status"] = "degraded"
    
    return status