"""
# POWER BI CONNECTION:
# 1. Open Power BI Desktop → Get Data → Web
# 2. URL: http://localhost:8000/export/summary.json
# 3. Add Authorization header with your JWT token
# 4. Refresh to get latest data
"""

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, extract, text
from datetime import datetime
import csv
import io
from typing import List, Dict, Any

from app.database import get_db
from app.models.user import User
from app.models.transaction import Transaction, TransactionType
from app.models.goal import Goal
from app.core.security import get_current_user

router = APIRouter()

@router.get("/transactions.csv")
async def export_transactions_csv(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Export all user transactions as CSV file"""
    
    # Query all transactions for the user
    result = await db.execute(
        select(Transaction)
        .where(Transaction.user_id == current_user.id)
        .order_by(Transaction.date.desc(), Transaction.created_at.desc())
    )
    transactions = result.scalars().all()
    
    # Create CSV content
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'Date', 'Description', 'Category', 'Amount', 'Type', 
        'Payment Mode', 'Account', 'Created At'
    ])
    
    # Write data rows
    for transaction in transactions:
        writer.writerow([
            transaction.date.strftime('%Y-%m-%d') if transaction.date else '',
            transaction.description or '',
            transaction.category or '',
            float(transaction.amount),
            transaction.transaction_type.value,
            transaction.payment_mode or '',
            transaction.account or '',
            transaction.created_at.strftime('%Y-%m-%d %H:%M:%S') if transaction.created_at else ''
        ])
    
    # Reset pointer to beginning
    output.seek(0)
    
    # Create streaming response
    response = StreamingResponse(
        io.BytesIO(output.getvalue().encode('utf-8')),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=transactions_{current_user.id}_{datetime.now().strftime('%Y%m%d')}.csv"
        }
    )
    
    return response


@router.get("/summary.json")
async def export_summary_json(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Export comprehensive data for Power BI in JSON format"""
    
    # Get all transactions
    transactions_result = await db.execute(
        select(Transaction)
        .where(Transaction.user_id == current_user.id)
        .order_by(Transaction.date.desc(), Transaction.created_at.desc())
    )
    transactions = transactions_result.scalars().all()
    
    # Get goals
    goals_result = await db.execute(
        select(Goal)
        .where(Goal.user_id == current_user.id)
        .order_by(Goal.created_at.desc())
    )
    goals = goals_result.scalars().all()
    
    # Calculate by_category aggregation
    category_query = await db.execute(
        select(
            Transaction.category,
            func.count(Transaction.id).label('count'),
            func.sum(Transaction.amount).label('total'),
            func.avg(Transaction.amount).label('avg')
        )
        .where(Transaction.user_id == current_user.id)
        .group_by(Transaction.category)
        .order_by(func.sum(Transaction.amount).desc())
    )
    by_category = {}
    for row in category_query:
        by_category[row.category or 'Uncategorized'] = {
            'total': float(row.total),
            'count': row.count,
            'avg': float(row.avg)
        }
    
    # Calculate by_month aggregation
    month_query = await db.execute(
        select(
            extract('year', Transaction.date).label('year'),
            extract('month', Transaction.date).label('month'),
            func.sum(
                func.case(
                    (Transaction.transaction_type == TransactionType.INCOME, Transaction.amount),
                    else_=0
                )
            ).label('income'),
            func.sum(
                func.case(
                    (Transaction.transaction_type == TransactionType.EXPENSE, Transaction.amount),
                    else_=0
                )
            ).label('expense')
        )
        .where(Transaction.user_id == current_user.id)
        .group_by(
            extract('year', Transaction.date),
            extract('month', Transaction.date)
        )
        .order_by(
            extract('year', Transaction.date).desc(),
            extract('month', Transaction.date).desc()
        )
    )
    by_month = []
    for row in month_query:
        income = float(row.income) if row.income else 0
        expense = float(row.expense) if row.expense else 0
        by_month.append({
            'month': f"{int(row.year)}-{int(row.month):02d}",
            'income': income,
            'expense': expense,
            'net': income - expense
        })
    
    # Calculate savings rate
    total_income = sum(float(t.amount) for t in transactions if t.transaction_type == TransactionType.INCOME)
    total_expense = sum(float(t.amount) for t in transactions if t.transaction_type == TransactionType.EXPENSE)
    savings_rate = ((total_income - total_expense) / total_income * 100) if total_income > 0 else 0
    
    # Get period info
    if transactions:
        dates = [t.date for t in transactions if t.date]
        period = {
            'start': min(dates).strftime('%Y-%m-%d'),
            'end': max(dates).strftime('%Y-%m-%d')
        }
    else:
        period = {'start': None, 'end': None}
    
    # Format transactions for JSON
    transactions_data = []
    for transaction in transactions:
        transactions_data.append({
            'id': transaction.id,
            'date': transaction.date.strftime('%Y-%m-%d') if transaction.date else None,
            'description': transaction.description,
            'category': transaction.category,
            'amount': float(transaction.amount),
            'type': transaction.transaction_type.value,
            'payment_mode': transaction.payment_mode,
            'account': transaction.account,
            'created_at': transaction.created_at.isoformat() if transaction.created_at else None
        })
    
    # Format goals for JSON
    goals_data = []
    for goal in goals:
        goals_data.append({
            'id': goal.id,
            'title': goal.title,
            'description': goal.description,
            'category': goal.category,
            'target_amount': float(goal.target_amount),
            'current_amount': float(goal.current_amount),
            'deadline': goal.deadline.strftime('%Y-%m-%d') if goal.deadline else None,
            'created_at': goal.created_at.isoformat() if goal.created_at else None,
            'progress': (float(goal.current_amount) / float(goal.target_amount) * 100) if goal.target_amount > 0 else 0
        })
    
    # Build comprehensive response
    export_data = {
        'user': {
            'name': current_user.full_name or current_user.username,
            'email': current_user.email,
            'currency': current_user.currency or 'INR'
        },
        'period': period,
        'transactions': transactions_data,
        'by_category': by_category,
        'by_month': by_month,
        'goals': goals_data,
        'savings_rate': round(savings_rate, 2),
        'exported_at': datetime.now().isoformat()
    }
    
    return export_data
