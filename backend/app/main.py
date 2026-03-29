from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from app.core.config import settings
from app.database.database import create_tables
from app.models import *  # must be before create_tables()
from app.routers import auth, category, transactions, analytics, goals, investments, chat, export

# Create database tables on startup
create_tables()

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
    return {"status": "ok", "app": "FinSight"}