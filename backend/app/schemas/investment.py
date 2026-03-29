from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

class InvestmentCreate(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=10)
    name: str = Field(..., min_length=1, max_length=200)
    quantity: float = Field(..., gt=0)
    average_buy_price: float = Field(..., gt=0)

class Holding(BaseModel):
    id: str
    symbol: str
    name: str
    quantity: float
    average_buy_price: float
    current_price: float
    current_value: float
    gain_loss_pct: float

class InvestmentOut(BaseModel):
    id: str
    user_id: int
    symbol: str
    name: str
    quantity: float
    average_buy_price: float
    created_at: datetime

    model_config = {"from_attributes": True}

class PortfolioValue(BaseModel):
    holdings: List[Holding]
    total_value: float
    total_gain_loss: float
    total_gain_loss_pct: float
    live_data: bool