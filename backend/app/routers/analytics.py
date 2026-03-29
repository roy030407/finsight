from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, and_, extract
from datetime import datetime, date
from typing import List, Optional

from app.database.database import get_db
from app.api.deps_auth import get_current_user
from app.models.transaction import Transaction, TransactionType
from app.models.user import User
from ml.classifier import classifier

router = APIRouter()

@router.post("/classify")
async def classify_transaction(
    description: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Classify transaction description using ML model"""
    try:
        predicted_category, confidence = classifier.predict_category(description)
        
        return {
            "category": predicted_category,
            "confidence": round(confidence, 3),
            "description": description
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Classification service unavailable"
        )

@router.get("/insights")
async def get_analytics_insights(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get spending insights and analytics for current user"""
    try:
        # Get user's transactions for analysis
        result = await db.execute(
            select(Transaction).where(Transaction.user_id == current_user.id)
        )
        transactions = result.scalars().all()
        
        if not transactions:
            return {
                "top_category": "No data",
                "unusual_transactions": [],
                "monthly_trend": "stable",
                "savings_rate": 0.0,
                "total_transactions": 0
            }
        
        # Calculate category totals
        category_totals = {}
        for transaction in transactions:
            category = transaction.category
            if category not in category_totals:
                category_totals[category] = {"count": 0, "total": 0.0, "avg": 0.0}
            
            category_totals[category]["count"] += 1
            category_totals[category]["total"] += float(transaction.amount)
        
        # Find top spending category (excluding income)
        expense_categories = {
            cat: data for cat, data in category_totals.items() 
            if any(expense_cat.lower() in cat.lower() for expense_cat in [
                "Food", "Transport", "Shopping", "Entertainment", 
                "Utilities", "Healthcare", "Education", "Other"
            ])
        }
        
        top_category = max(expense_categories.items(), key=lambda x: x[1]["total"]) if expense_categories else ("No data", {})
        
        # Calculate average per category for unusual detection
        category_averages = {
            cat: data["total"] / data["count"] 
            for cat, data in category_totals.items()
        }
        
        # Find unusual transactions (more than 2x average for that category)
        unusual_transactions = []
        for transaction in transactions:
            if transaction.type == TransactionType.EXPENSE:
                avg_for_category = category_averages.get(transaction.category, 0)
                if avg_for_category > 0 and float(transaction.amount) > (2 * avg_for_category):
                    unusual_transactions.append({
                        "id": str(transaction.id),
                        "description": transaction.description or transaction.category,
                        "category": transaction.category,
                        "amount": float(transaction.amount),
                        "date": transaction.date.isoformat(),
                        "unusual_factor": round(float(transaction.amount) / avg_for_category, 1)
                    })
        
        # Sort unusual transactions by amount (highest first)
        unusual_transactions.sort(key=lambda x: x["amount"], reverse=True)
        unusual_transactions = unusual_transactions[:5]  # Top 5 unusual
        
        # Calculate monthly trend (last 3 months)
        current_date = datetime.now()
        three_months_ago = current_date.replace(month=current_date.month - 3)
        
        recent_transactions = [
            t for t in transactions 
            if t.date >= three_months_ago.date()
        ]
        
        if len(recent_transactions) >= 2:
            # Calculate month-over-month trend
            monthly_amounts = {}
            for transaction in recent_transactions:
                month_key = transaction.date.strftime("%Y-%m")
                if month_key not in monthly_amounts:
                    monthly_amounts[month_key] = {"income": 0.0, "expenses": 0.0}
                
                if transaction.type == TransactionType.INCOME:
                    monthly_amounts[month_key]["income"] += float(transaction.amount)
                else:
                    monthly_amounts[month_key]["expenses"] += float(transaction.amount)
            
            months = sorted(monthly_amounts.keys())
            if len(months) >= 2:
                latest_month = monthly_amounts[months[-1]]
                previous_month = monthly_amounts[months[-2]]
                
                latest_savings = latest_month["income"] - latest_month["expenses"]
                previous_savings = previous_month["income"] - previous_month["expenses"]
                
                if previous_savings > 0:
                    change_percent = ((latest_savings - previous_savings) / previous_savings) * 100
                    if change_percent > 5:
                        monthly_trend = "increasing"
                    elif change_percent < -5:
                        monthly_trend = "decreasing"
                    else:
                        monthly_trend = "stable"
                else:
                    monthly_trend = "stable"
            else:
                monthly_trend = "stable"
        else:
            monthly_trend = "stable"
        
        # Calculate savings rate
        total_income = sum(t.amount for t in transactions if t.type == TransactionType.INCOME)
        total_expenses = sum(t.amount for t in transactions if t.type == TransactionType.EXPENSE)
        
        savings_rate = ((total_income - total_expenses) / total_income * 100) if total_income > 0 else 0
        
        return {
            "top_category": top_category[0] if isinstance(top_category, tuple) else "No data",
            "unusual_transactions": unusual_transactions,
            "monthly_trend": monthly_trend,
            "savings_rate": round(savings_rate, 2),
            "total_transactions": len(transactions),
            "category_breakdown": {
                cat: {
                    "count": data["count"],
                    "total": round(data["total"], 2),
                    "average": round(data["average"], 2)
                }
                for cat, data in category_totals.items()
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Failed to generate insights"
        )
