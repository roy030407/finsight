from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
from datetime import datetime, timedelta
from typing import List, Optional
import os

from app.database.database import get_db
from app.models.user import User
from app.schemas.goal import GoalCreate, GoalUpdate, GoalOut
from app.api.deps_auth import get_current_user

router = APIRouter(prefix="/goals", tags=["goals"])

# Helper function to calculate days until deadline
def days_until_deadline(deadline: datetime) -> int:
    """Calculate days remaining until deadline"""
    if not deadline:
        return None
    today = datetime.now().date()
    deadline_date = deadline.date()
    return (deadline_date - today).days

@router.post("/", response_model=GoalOut)
async def create_goal(
    goal: GoalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new financial goal"""
    db_goal = {
        "user_id": current_user.id,
        "title": goal.title,
        "description": goal.description,
        "target_amount": goal.target_amount,
        "current_amount": goal.current_amount or 0,
        "category": goal.category,
        "deadline": goal.deadline,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "is_completed": False
    }
    
    # In a real implementation, this would save to database
    # For now, return the created goal
    return GoalOut.model_validate(db_goal)

@router.get("/", response_model=List[GoalOut])
async def list_goals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all goals for the current user"""
    # Mock data for demonstration
    mock_goals = [
        {
            "id": "1",
            "user_id": current_user.id,
            "title": "Emergency Fund",
            "description": "Build 6 months of expenses",
            "target_amount": 300000.00,
            "current_amount": 150000.00,
            "category": "Emergency",
            "deadline": datetime.now() + timedelta(days=90),
            "created_at": datetime.now() - timedelta(days=30),
            "updated_at": datetime.now(),
            "is_completed": False
        },
        {
            "id": "2", 
            "user_id": current_user.id,
            "title": "Vacation Fund",
            "description": "Trip to Europe",
            "target_amount": 200000.00,
            "current_amount": 80000.00,
            "category": "Travel",
            "deadline": datetime.now() + timedelta(days=180),
            "created_at": datetime.now() - timedelta(days=60),
            "updated_at": datetime.now(),
            "is_completed": False
        }
    ]
    
    return [GoalOut.model_validate(goal) for goal in mock_goals]

@router.put("/{goal_id}", response_model=GoalOut)
async def update_goal(
    goal_id: str,
    goal_update: GoalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a goal (including current_amount for progress tracking)"""
    # In a real implementation, this would update the database
    # For now, return updated mock data
    updated_goal = {
        "id": goal_id,
        "user_id": current_user.id,
        "title": goal_update.title,
        "description": goal_update.description,
        "target_amount": goal_update.target_amount,
        "current_amount": goal_update.current_amount,
        "category": goal_update.category,
        "deadline": goal_update.deadline,
        "created_at": datetime.now() - timedelta(days=30),
        "updated_at": datetime.now(),
        "is_completed": goal_update.current_amount >= goal_update.target_amount if goal_update.current_amount and goal_update.target_amount else False
    }
    
    return GoalOut.model_validate(updated_goal)

@router.delete("/{goal_id}")
async def delete_goal(
    goal_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a goal"""
    # In a real implementation, this would delete from database
    # For now, just return success
    return {"message": "Goal deleted successfully"}
