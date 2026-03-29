from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field


class TransactionBase(BaseModel):
    amount: float = Field(..., gt=0)
    transaction_type: str = Field(..., pattern="^(income|expense)$")
    category: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    transaction_date: date = Field(...)
    payment_mode: Optional[str] = Field(None, max_length=50)
    account: Optional[str] = Field(None, max_length=100)
    blockchain_hash: Optional[str] = Field(None, max_length=64)


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(BaseModel):
    amount: Optional[float] = Field(None, gt=0)
    transaction_type: Optional[str] = Field(None, pattern="^(income|expense)$")
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    transaction_date: Optional[date] = None
    payment_mode: Optional[str] = Field(None, max_length=50)
    account: Optional[str] = Field(None, max_length=100)


class TransactionOut(TransactionBase):
    id: str
    user_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class CategorySummary(BaseModel):
    category: str
    total_amount: float
    count: int


class MonthlySummary(BaseModel):
    month: str
    income: float
    expenses: float
    net: float


class TransactionSummary(BaseModel):
    total_income: float
    total_expenses: float
    net_cashflow: float
    by_category: List[CategorySummary]
    by_month: List[MonthlySummary]