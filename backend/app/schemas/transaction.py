from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field
from pydantic import field_validator, model_validator


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


class TransactionOut(BaseModel):
    id: str
    user_id: int
    amount: float
    transaction_type: str
    category: str
    description: Optional[str] = None
    transaction_date: str
    payment_mode: Optional[str] = None
    account: Optional[str] = None
    blockchain_hash: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}

    @model_validator(mode='before')
    @classmethod
    def map_fields(cls, obj):
        if hasattr(obj, '__dict__') or hasattr(obj, 'type'):
            return {
                'id': str(obj.id),
                'user_id': obj.user_id,
                'amount': float(round(obj.amount, 2)),
                'transaction_type': obj.type.value if hasattr(obj.type, 'value') else str(obj.type),
                'category': obj.category,
                'description': obj.description,
                'transaction_date': str(obj.date),
                'payment_mode': obj.payment_mode,
                'account': obj.account,
                'blockchain_hash': obj.blockchain_hash,
                'created_at': obj.created_at,
            }
        return obj


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