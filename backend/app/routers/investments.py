from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
from datetime import datetime, timedelta
from typing import List, Optional
import os
import requests
import json

from app.database.database import get_db
from app.models.user import User
from app.schemas.investment import InvestmentCreate, InvestmentOut, PortfolioValue
from app.api.deps_auth import get_current_user

router = APIRouter(prefix="/investments", tags=["investments"])

# Alpha Vantage API configuration
ALPHA_VANTAGE_KEY = os.getenv("ALPHA_VANTAGE_KEY")
ALPHA_VANTAGE_URL = "https://www.alphavantage.co/query"

def get_current_price(symbol: str) -> Optional[float]:
    """Fetch current price from Alpha Vantage API"""
    if not ALPHA_VANTAGE_KEY:
        print("Alpha Vantage API key not found, using mock price")
        return None
    
    try:
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": ALPHA_VANTAGE_KEY
        }
        
        response = requests.get(ALPHA_VANTAGE_URL, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        if "Global Quote" in data and "05. price" in data["Global Quote"]:
            return float(data["Global Quote"]["05. price"])
        
        print(f"Invalid response for {symbol}: {data}")
        return None
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching price for {symbol}: {e}")
        return None
    except (KeyError, ValueError) as e:
        print(f"Error parsing price data for {symbol}: {e}")
        return None

def get_mock_price(symbol: str) -> float:
    """Return mock price for demonstration"""
    mock_prices = {
        "AAPL": 150.25,
        "GOOGL": 2800.50,
        "MSFT": 305.75,
        "TSLA": 850.00,
        "AMZN": 3200.00,
        "NVDA": 220.50,
        "META": 325.00,
        "BTC": 45000.00,
        "ETH": 2800.00
    }
    return mock_prices.get(symbol.upper(), 100.00)

@router.post("/", response_model=InvestmentOut)
async def create_investment(
    investment: InvestmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a new investment holding"""
    db_investment = {
        "id": str(len(investment.symbol) + str(datetime.now().timestamp())),
        "user_id": current_user.id,
        "symbol": investment.symbol.upper(),
        "name": investment.name,
        "quantity": investment.quantity,
        "average_buy_price": investment.average_buy_price,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    
    # In a real implementation, this would save to database
    return InvestmentOut.model_validate(db_investment)

@router.get("/", response_model=List[InvestmentOut])
async def list_investments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all investment holdings for the current user"""
    # Mock data for demonstration
    mock_investments = [
        {
            "id": "1",
            "user_id": current_user.id,
            "symbol": "AAPL",
            "name": "Apple Inc.",
            "quantity": 10,
            "average_buy_price": 145.50,
            "created_at": datetime.now() - timedelta(days=90),
            "updated_at": datetime.now()
        },
        {
            "id": "2",
            "user_id": current_user.id,
            "symbol": "GOOGL", 
            "name": "Alphabet Inc.",
            "quantity": 5,
            "average_buy_price": 2750.00,
            "created_at": datetime.now() - timedelta(days=60),
            "updated_at": datetime.now()
        },
        {
            "id": "3",
            "user_id": current_user.id,
            "symbol": "MSFT",
            "name": "Microsoft Corporation",
            "quantity": 15,
            "average_buy_price": 295.25,
            "created_at": datetime.now() - timedelta(days=30),
            "updated_at": datetime.now()
        }
    ]
    
    return [InvestmentOut.model_validate(inv) for inv in mock_investments]

@router.delete("/{investment_id}")
async def delete_investment(
    investment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an investment holding"""
    # In a real implementation, this would delete from database
    return {"message": "Investment deleted successfully"}

@router.get("/portfolio-value", response_model=PortfolioValue)
async def get_portfolio_value(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get portfolio value with current prices from Alpha Vantage API"""
    # Get user's investments
    investments = await list_investments(db=db, current_user=current_user)
    
    holdings = []
    total_value = 0.0
    total_cost = 0.0
    live_data = True
    
    for inv in investments:
        # Try to get current price from API
        current_price = get_current_price(inv.symbol)
        
        if current_price is None:
            # Fallback to mock price
            current_price = get_mock_price(inv.symbol)
            live_data = False
        
        current_value = inv.quantity * current_price
        cost_basis = inv.quantity * inv.average_buy_price
        gain_loss = current_value - cost_basis
        gain_loss_pct = (gain_loss / cost_basis * 100) if cost_basis > 0 else 0
        
        holding = {
            "id": inv.id,
            "symbol": inv.symbol,
            "name": inv.name,
            "quantity": inv.quantity,
            "average_buy_price": inv.average_buy_price,
            "current_price": current_price,
            "current_value": current_value,
            "gain_loss_pct": round(gain_loss_pct, 2)
        }
        
        holdings.append(holding)
        total_value += current_value
        total_cost += cost_basis
    
    total_gain_loss = total_value - total_cost
    total_gain_loss_pct = (total_gain_loss / total_cost * 100) if total_cost > 0 else 0
    
    return PortfolioValue(
        holdings=holdings,
        total_value=round(total_value, 2),
        total_gain_loss=round(total_gain_loss, 2),
        total_gain_loss_pct=round(total_gain_loss_pct, 2),
        live_data=live_data
    )
