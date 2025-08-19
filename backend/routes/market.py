from fastapi import APIRouter, HTTPException
import yfinance as yf
from database import db
from datetime import datetime, timezone
from services.stock_service import stock_service
from services.chatbot_service import chatbot_service
from models.stock import StockOrder, OrderType, OrderStatus
from typing import List
from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str
    user_id: str = "default_user"

router = APIRouter(prefix="/market", tags=["Market"])

@router.get("/stock/{symbol}")
async def get_stock_data(symbol: str):
    """Get comprehensive stock data for a symbol"""
    try:
        stock_data = await stock_service.get_stock_data(symbol)
        return {"status": "success", "data": stock_data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/analytics/{symbol}")
async def get_stock_analytics(symbol: str):
    """Get comprehensive stock analytics including technical indicators"""
    try:
        analytics = await stock_service.get_stock_analytics(symbol)
        return {"status": "success", "data": analytics}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/order")
async def place_order(order: StockOrder):
    """Place a buy or sell order"""
    try:
        placed_order = await stock_service.place_order(order)
        return {"status": "success", "data": placed_order}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/order/{order_id}/execute")
async def execute_order(order_id: str):
    """Execute a pending order"""
    try:
        executed_order = await stock_service.execute_order(order_id)
        return {"status": "success", "data": executed_order}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/portfolio/{user_id}")
async def get_portfolio(user_id: str):
    """Get user's portfolio"""
    try:
        portfolio = await stock_service.get_portfolio(user_id)
        return {"status": "success", "data": portfolio}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/chat")
async def chat_with_bot(chat_request: ChatRequest):
    """Chat with the stock trading bot using natural language"""
    try:
        response = await chatbot_service.process_message(chat_request.message, chat_request.user_id)
        return {
            "status": "success",
            "data": {
                "message": chat_request.message,
                "response": response,
                "user_id": chat_request.user_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/chat/help")
async def get_chat_help():
    """Get help information for the chatbot"""
    return {
        "status": "success",
        "data": {
            "help": chatbot_service.help_text,
            "examples": [
                "Buy 10 shares of AAPL",
                "Sell 5 MSFT",
                "What is the price of TSLA?",
                "Analyze GOOGL",
                "Show my portfolio",
                "Help"
            ]
        }
    }
