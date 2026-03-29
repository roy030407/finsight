import os
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel

from app.database.database import get_db
from app.models.user import User
from app.api.deps_auth import get_current_user
from rag.pipeline import rag_pipeline


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str
    sources_used: int


router = APIRouter(tags=["ai-chat"])


async def log_conversation_to_mongo(user_id: int, message: str, reply: str, sources_used: int):
    """Log conversation to MongoDB if MONGO_URL is configured"""
    try:
        mongo_url = os.getenv("MONGO_URL")
        if not mongo_url:
            return  # Skip silently if not configured
        
        # Import here to avoid dependency if not configured
        from motor.motor_asyncio import AsyncIOMotorClient
        
        client = AsyncIOMotorClient(mongo_url)
        db = client.finsight
        collection = db.chat_logs
        
        await collection.insert_one({
            "user_id": user_id,
            "message": message,
            "reply": reply,
            "sources_used": sources_used,
            "timestamp": None  # Will use MongoDB's default timestamp
        })
        
        await client.close()
        
    except Exception as e:
        # Log errors but don't fail the chat response
        print(f"Failed to log conversation to MongoDB: {e}")


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Chat endpoint for AI-powered financial assistance
    """
    try:
        # Get user's financial context
        user_context = rag_pipeline.get_user_context(current_user.id, db)
        
        # Get AI response
        result = await rag_pipeline.answer_finance_question(
            question=request.message,
            user_context=user_context
        )
        
        # Log conversation asynchronously (don't wait for it)
        import asyncio
        asyncio.create_task(
            log_conversation_to_mongo(
                user_id=current_user.id,
                message=request.message,
                reply=result["answer"],
                sources_used=result["sources_used"]
            )
        )
        
        return ChatResponse(
            reply=result["answer"],
            sources_used=result["sources_used"]
        )
        
    except Exception as e:
        # Never expose raw errors to frontend
        print(f"Chat endpoint error: {e}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your request. Please try again."
        )
