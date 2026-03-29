import hashlib
import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, extract, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database.database import get_db
from app.models.transaction import Transaction, TransactionType
from app.models.blockchain_ledger import BlockchainLedger
from app.schemas.transaction import (
    TransactionCreate, TransactionUpdate, TransactionOut, TransactionSummary,
    CategorySummary, MonthlySummary
)
from app.api.deps_auth import get_current_user
from app.models.user import User

from sqlalchemy import case
from sqlalchemy import and_, extract, func, or_

router = APIRouter()


async def get_previous_hash(db: AsyncSession) -> str:
    """Get the most recent hash from blockchain ledger"""
    result = await db.execute(
        select(BlockchainLedger)
        .order_by(BlockchainLedger.block_index.desc())
        .limit(1)
    )
    last_block = result.scalar_one_or_none()
    return last_block.current_hash if last_block else "0" * 64


async def create_blockchain_entry(
    db: AsyncSession, 
    transaction_id: uuid.UUID, 
    amount: Decimal, 
    transaction_date: date,
    previous_hash: str
) -> str:
    """Create blockchain entry for transaction"""
    # Get next block index
    result = await db.execute(
        select(func.count(BlockchainLedger.id))
    )
    block_index = result.scalar() or 0
    
    # Compute hash
    hash_input = f"{transaction_id}{amount}{transaction_date}{previous_hash}"
    current_hash = hashlib.sha256(hash_input.encode()).hexdigest()
    
    # Find nonce (simple proof of work)
    nonce = 0
    while not current_hash.startswith("0000"):  # Simple difficulty
        nonce += 1
        hash_input_with_nonce = f"{hash_input}{nonce}"
        current_hash = hashlib.sha256(hash_input_with_nonce.encode()).hexdigest()
    
    # Create blockchain entry
    blockchain_entry = BlockchainLedger(
        transaction_id=transaction_id,
        block_index=block_index,
        previous_hash=previous_hash,
        current_hash=current_hash,
        nonce=nonce
    )
    db.add(blockchain_entry)
    
    return current_hash


@router.post("/", response_model=TransactionOut, status_code=201)
async def create_transaction(
    transaction: TransactionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new transaction with blockchain hash"""
    # Create transaction
    db_transaction = Transaction(
        user_id=current_user.id,
        amount=Decimal(str(transaction.amount)),
        type=TransactionType(transaction.transaction_type),
        category=transaction.category,
        description=transaction.description,
        date=transaction.transaction_date,
        payment_mode=transaction.payment_mode,
        account=getattr(transaction, 'account', None)
    )
    db.add(db_transaction)
    await db.flush()  # Get the ID without committing
    
    # Create blockchain entry
    previous_hash = await get_previous_hash(db)
    blockchain_hash = await create_blockchain_entry(
        db, db_transaction.id, db_transaction.amount, db_transaction.date, previous_hash
    )
    
    # Update transaction with blockchain hash
    db_transaction.blockchain_hash = blockchain_hash
    
    await db.commit()
    await db.refresh(db_transaction)
    
    return TransactionOut.model_validate(db_transaction)


@router.get("/", response_model=List[TransactionOut])
async def list_transactions(
    category: Optional[str] = Query(None, description="Filter by category"),
    type: Optional[str] = Query(None, regex="^(income|expense)$", description="Filter by type"),
    start_date: Optional[date] = Query(None, description="Filter by start date"),
    end_date: Optional[date] = Query(None, description="Filter by end date"),
    min_amount: Optional[float] = Query(None, ge=0, description="Minimum amount"),
    max_amount: Optional[float] = Query(None, ge=0, description="Maximum amount"),
    limit: int = Query(50, ge=1, le=1000, description="Number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List transactions for current user with filtering"""
    query = select(Transaction).where(Transaction.user_id == current_user.id)
    
    # Apply filters
    if category:
        query = query.where(Transaction.category.ilike(f"%{category}%"))
    if type:
        query = query.where(Transaction.type == TransactionType(type))
    if start_date:
        query = query.where(Transaction.date >= start_date)
    if end_date:
        query = query.where(Transaction.date <= end_date)
    if min_amount:
        query = query.where(Transaction.amount >= Decimal(str(min_amount)))
    if max_amount:
        query = query.where(Transaction.amount <= Decimal(str(max_amount)))
    
    # Order and paginate
    query = query.order_by(Transaction.date.desc(), Transaction.created_at.desc())
    query = query.offset(offset).limit(limit)
    
    result = await db.execute(query)
    transactions = result.scalars().all()
    
    return [TransactionOut.model_validate(t) for t in transactions]


@router.put("/{transaction_id}", response_model=TransactionOut)
async def update_transaction(
    transaction_id: uuid.UUID,
    transaction_update: TransactionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a transaction (user must own it)"""
    # Get existing transaction
    result = await db.execute(
        select(Transaction).where(
            and_(
                Transaction.id == transaction_id,
                Transaction.user_id == current_user.id
            )
        )
    )
    transaction = result.scalar_one_or_none()
    
    if not transaction:
        raise HTTPException(
            status_code=404, 
            detail="Transaction not found or you don't have permission to access it"
        )
    
    # Update fields
    update_data = transaction_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field == "type" and value:
            setattr(transaction, field, TransactionType(value))
        elif field == "amount" and value:
            setattr(transaction, field, Decimal(str(value)))
        elif field == "date" and value:
            setattr(transaction, field, value)
        elif value is not None:
            setattr(transaction, field, value)
    
    await db.commit()
    await db.refresh(transaction)
    
    return TransactionOut.from_orm(transaction)


@router.delete("/{transaction_id}", status_code=204)
async def delete_transaction(
    transaction_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a transaction (user must own it)"""
    # Get existing transaction
    result = await db.execute(
        select(Transaction).where(
            and_(
                Transaction.id == transaction_id,
                Transaction.user_id == current_user.id
            )
        )
    )
    transaction = result.scalar_one_or_none()
    
    if not transaction:
        raise HTTPException(
            status_code=404, 
            detail="Transaction not found or you don't have permission to access it"
        )
    
    await db.delete(transaction)
    await db.commit()


@router.get("/summary", response_model=TransactionSummary)
async def get_transaction_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get transaction summary for current user"""
    
    # Total income and expenses
    result = await db.execute(
        select(
            Transaction.type,
            func.sum(Transaction.amount).label("total")
        )
        .where(Transaction.user_id == current_user.id)
        .group_by(Transaction.type)
    )
    totals = result.all()
    
    total_income = 0.0
    total_expenses = 0.0
    
    for type_val, total in totals:
        if type_val == TransactionType.INCOME:
            total_income = float(round(total, 2))
        else:
            total_expenses = float(round(total, 2))
    
    net_cashflow = total_income - total_expenses
    
    # Summary by category
    result = await db.execute(
        select(
            Transaction.category,
            func.sum(Transaction.amount).label("total_amount"),
            func.count(Transaction.id).label("count")
        )
        .where(Transaction.user_id == current_user.id)
        .group_by(Transaction.category)
        .order_by(func.sum(Transaction.amount).desc())
    )
    by_category = [
        CategorySummary(
            category=category,
            total_amount=float(round(total_amount, 2)),
            count=count
        )
        for category, total_amount, count in result.all()
    ]
    
    # Summary by month
    result = await db.execute(
        select(
            extract('year', Transaction.date).label('year'),
            extract('month', Transaction.date).label('month'),
            func.sum(case((Transaction.type == TransactionType.INCOME, Transaction.amount), else_=0)).label('income'),
            func.sum(case((Transaction.type == TransactionType.EXPENSE, Transaction.amount), else_=0)).label('expenses')
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
    for year, month, income, expenses in result.all():
        month_str = f"{int(year):04d}-{int(month):02d}"
        by_month.append(
            MonthlySummary(
                month=month_str,
                income=float(round(income, 2)),
                expenses=float(round(expenses, 2)),
                net=float(round(income - expenses, 2))
            )
        )
    
    return TransactionSummary(
        total_income=total_income,
        total_expenses=total_expenses,
        net_cashflow=net_cashflow,
        by_category=by_category,
        by_month=by_month
    )

@router.get("/{transaction_id}", response_model=TransactionOut)
async def get_transaction(
    transaction_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a single transaction"""
    result = await db.execute(
        select(Transaction).where(
            and_(
                Transaction.id == transaction_id,
                Transaction.user_id == current_user.id
            )
        )
    )
    transaction = result.scalar_one_or_none()
    
    if not transaction:
        raise HTTPException(
            status_code=404, 
            detail="Transaction not found or you don't have permission to access it"
        )
    
    return TransactionOut.model_validate(transaction)