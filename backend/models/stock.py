from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class OrderType(str, Enum):
    BUY = "buy"
    SELL = "sell"

class OrderStatus(str, Enum):
    PENDING = "pending"
    EXECUTED = "executed"
    CANCELLED = "cancelled"
    FAILED = "failed"

class StockData(BaseModel):
    symbol: str
    price: float
    volume: int
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    previous_close: float
    change: float
    change_percent: float
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    dividend_yield: Optional[float] = None
    timestamp: datetime

class StockOrder(BaseModel):
    id: Optional[str] = None
    symbol: str
    order_type: OrderType
    quantity: int
    price: float
    total_amount: float
    status: OrderStatus = OrderStatus.PENDING
    timestamp: Optional[datetime] = None
    user_id: Optional[str] = None
    notes: Optional[str] = None

class Portfolio(BaseModel):
    user_id: str
    symbol: str
    quantity: int
    average_price: float
    total_invested: float
    current_value: float
    unrealized_pnl: float
    last_updated: datetime

class StockAnalytics(BaseModel):
    symbol: str
    technical_indicators: Dict[str, Any]
    fundamental_metrics: Dict[str, Any]
    price_history: List[Dict[str, Any]]
    recommendations: List[str]
    risk_score: float
    timestamp: datetime

class ChatMessage(BaseModel):
    id: Optional[str] = None
    user_id: str
    message: str
    response: str
    timestamp: datetime
    context: Optional[Dict[str, Any]] = None
