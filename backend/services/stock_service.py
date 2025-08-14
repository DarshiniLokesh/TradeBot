import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple
from models.stock import StockData, StockOrder, Portfolio, StockAnalytics, OrderType, OrderStatus
from database import db
import asyncio

class StockService:
    def __init__(self):
        self.cache = {}
        self.cache_timeout = 300  # 5 minutes

    async def get_stock_data(self, symbol: str) -> StockData:
        """Get comprehensive stock data including real-time price and metrics"""
        try:
            symbol = symbol.strip().upper()
            
            # Check cache first
            cache_key = f"stock_{symbol}"
            if cache_key in self.cache:
                cached_data, timestamp = self.cache[cache_key]
                if (datetime.now(timezone.utc) - timestamp).seconds < self.cache_timeout:
                    return cached_data

            stock = yf.Ticker(symbol)
            
            # Get current data
            hist = stock.history(period="2d")
            if hist.empty:
                raise ValueError(f"No data found for symbol {symbol}")

            # Get additional info
            info = stock.info
            
            current_row = hist.iloc[-1]
            previous_row = hist.iloc[-2] if len(hist) > 1 else current_row
            
            change = current_row["Close"] - previous_row["Close"]
            change_percent = (change / previous_row["Close"]) * 100 if previous_row["Close"] != 0 else 0
            
            stock_data = StockData(
                symbol=symbol,
                price=float(current_row["Close"]),
                volume=int(current_row["Volume"]),
                open_price=float(current_row["Open"]),
                high_price=float(current_row["High"]),
                low_price=float(current_row["Low"]),
                close_price=float(current_row["Close"]),
                previous_close=float(previous_row["Close"]),
                change=float(change),
                change_percent=float(change_percent),
                market_cap=info.get('marketCap'),
                pe_ratio=info.get('trailingPE'),
                dividend_yield=info.get('dividendYield'),
                timestamp=datetime.now(timezone.utc)
            )

            # Cache the data
            self.cache[cache_key] = (stock_data, datetime.now(timezone.utc))
            
            # Store in database
            if db is not None:
                try:
                    await db.stocks.insert_one(stock_data.dict())
                except Exception as e:
                    print(f"Failed to store stock data: {e}")

            return stock_data

        except Exception as e:
            raise Exception(f"Failed to get stock data: {str(e)}")

    async def place_order(self, order: StockOrder) -> StockOrder:
        """Place a buy or sell order"""
        try:
            # Validate order
            if order.quantity <= 0:
                raise ValueError("Quantity must be positive")
            if order.price <= 0:
                raise ValueError("Price must be positive")

            # Get current stock price
            current_data = await self.get_stock_data(order.symbol)
            
            # Update order with current timestamp and calculated total
            order.timestamp = datetime.now(timezone.utc)
            order.total_amount = order.quantity * order.price
            
            # Store order in database
            if db is not None:
                result = await db.orders.insert_one(order.dict())
                order.id = str(result.inserted_id)
                
                # Update portfolio if order is executed
                if order.status == OrderStatus.EXECUTED:
                    await self._update_portfolio(order)
            else:
                order.id = f"order_{datetime.now().timestamp()}"

            return order

        except Exception as e:
            raise Exception(f"Failed to place order: {str(e)}")

    async def execute_order(self, order_id: str) -> StockOrder:
        """Execute a pending order"""
        try:
            if db is None:
                raise Exception("Database not available")

            # Find and update order
            result = await db.orders.update_one(
                {"_id": order_id},
                {"$set": {"status": OrderStatus.EXECUTED}}
            )
            
            if result.modified_count == 0:
                raise Exception("Order not found or already executed")

            # Get updated order
            order_doc = await db.orders.find_one({"_id": order_id})
            order = StockOrder(**order_doc)
            
            # Update portfolio
            await self._update_portfolio(order)
            
            return order

        except Exception as e:
            raise Exception(f"Failed to execute order: {str(e)}")

    async def get_portfolio(self, user_id: str) -> List[Portfolio]:
        """Get user's portfolio"""
        try:
            if db is None:
                return []

            portfolio_docs = await db.portfolio.find({"user_id": user_id}).to_list(None)
            portfolios = []
            
            for doc in portfolio_docs:
                # Get current stock data to update values
                try:
                    current_data = await self.get_stock_data(doc["symbol"])
                    current_value = doc["quantity"] * current_data.price
                    unrealized_pnl = current_value - doc["total_invested"]
                    
                    portfolio = Portfolio(
                        user_id=doc["user_id"],
                        symbol=doc["symbol"],
                        quantity=doc["quantity"],
                        average_price=doc["average_price"],
                        total_invested=doc["total_invested"],
                        current_value=current_value,
                        unrealized_pnl=unrealized_pnl,
                        last_updated=datetime.now(timezone.utc)
                    )
                    portfolios.append(portfolio)
                except Exception as e:
                    print(f"Failed to update portfolio for {doc['symbol']}: {e}")

            return portfolios

        except Exception as e:
            raise Exception(f"Failed to get portfolio: {str(e)}")

    async def get_stock_analytics(self, symbol: str) -> StockAnalytics:
        """Get comprehensive stock analytics including technical indicators"""
        try:
            stock = yf.Ticker(symbol)
            
            # Get historical data
            hist = stock.history(period="1y")
            if hist.empty:
                raise ValueError(f"No historical data for {symbol}")

            # Calculate technical indicators
            technical_indicators = self._calculate_technical_indicators(hist)
            
            # Get fundamental metrics
            info = stock.info
            fundamental_metrics = {
                "market_cap": info.get('marketCap'),
                "pe_ratio": info.get('trailingPE'),
                "pb_ratio": info.get('priceToBook'),
                "debt_to_equity": info.get('debtToEquity'),
                "return_on_equity": info.get('returnOnEquity'),
                "profit_margins": info.get('profitMargins'),
                "revenue_growth": info.get('revenueGrowth'),
                "earnings_growth": info.get('earningsGrowth')
            }

            # Generate price history
            price_history = []
            for date, row in hist.tail(30).iterrows():  # Last 30 days
                price_history.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "close": float(row["Close"]),
                    "volume": int(row["Volume"])
                })

            # Generate recommendations
            recommendations = self._generate_recommendations(technical_indicators, fundamental_metrics)
            
            # Calculate risk score
            risk_score = self._calculate_risk_score(technical_indicators, fundamental_metrics)

            analytics = StockAnalytics(
                symbol=symbol,
                technical_indicators=technical_indicators,
                fundamental_metrics=fundamental_metrics,
                price_history=price_history,
                recommendations=recommendations,
                risk_score=risk_score,
                timestamp=datetime.now(timezone.utc)
            )

            return analytics

        except Exception as e:
            raise Exception(f"Failed to get analytics: {str(e)}")

    def _calculate_technical_indicators(self, hist: pd.DataFrame) -> Dict[str, float]:
        """Calculate technical indicators from historical data"""
        try:
            close_prices = hist['Close']
            
            # Moving averages
            sma_20 = close_prices.rolling(window=20).mean().iloc[-1]
            sma_50 = close_prices.rolling(window=50).mean().iloc[-1]
            
            # RSI
            delta = close_prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs.iloc[-1]))
            
            # MACD
            ema_12 = close_prices.ewm(span=12).mean()
            ema_26 = close_prices.ewm(span=26).mean()
            macd = ema_12.iloc[-1] - ema_26.iloc[-1]
            signal = (ema_12 - ema_26).ewm(span=9).mean().iloc[-1]
            
            # Bollinger Bands
            bb_20 = close_prices.rolling(window=20).mean().iloc[-1]
            bb_std = close_prices.rolling(window=20).std().iloc[-1]
            bb_upper = bb_20 + (bb_std * 2)
            bb_lower = bb_20 - (bb_std * 2)
            
            return {
                "sma_20": float(sma_20) if not pd.isna(sma_20) else 0,
                "sma_50": float(sma_50) if not pd.isna(sma_50) else 0,
                "rsi": float(rsi) if not pd.isna(rsi) else 50,
                "macd": float(macd) if not pd.isna(macd) else 0,
                "macd_signal": float(signal) if not pd.isna(signal) else 0,
                "bb_upper": float(bb_upper) if not pd.isna(bb_upper) else 0,
                "bb_lower": float(bb_lower) if not pd.isna(bb_lower) else 0,
                "bb_middle": float(bb_20) if not pd.isna(bb_20) else 0
            }
        except Exception as e:
            print(f"Error calculating technical indicators: {e}")
            return {}

    def _generate_recommendations(self, technical: Dict, fundamental: Dict) -> List[str]:
        """Generate trading recommendations based on indicators"""
        recommendations = []
        
        try:
            # Technical analysis recommendations
            if technical.get("rsi", 50) < 30:
                recommendations.append("RSI indicates oversold conditions - potential buy signal")
            elif technical.get("rsi", 50) > 70:
                recommendations.append("RSI indicates overbought conditions - consider taking profits")
            
            if technical.get("macd", 0) > technical.get("macd_signal", 0):
                recommendations.append("MACD is above signal line - bullish momentum")
            else:
                recommendations.append("MACD is below signal line - bearish momentum")
            
            # Fundamental analysis recommendations
            if fundamental.get("pe_ratio", 0) < 15:
                recommendations.append("Low P/E ratio suggests good value")
            elif fundamental.get("pe_ratio", 0) > 25:
                recommendations.append("High P/E ratio - evaluate growth prospects")
            
            if fundamental.get("debt_to_equity", 0) > 1:
                recommendations.append("High debt levels - increased risk")
            
            if not recommendations:
                recommendations.append("No strong signals - maintain current position")
                
        except Exception as e:
            recommendations.append("Unable to generate recommendations")
            
        return recommendations

    def _calculate_risk_score(self, technical: Dict, fundamental: Dict) -> float:
        """Calculate risk score from 0 (low risk) to 100 (high risk)"""
        try:
            risk_score = 50  # Base risk score
            
            # Technical risk factors
            rsi = technical.get("rsi", 50)
            if rsi < 20 or rsi > 80:
                risk_score += 20  # Extreme RSI values
            
            # Fundamental risk factors
            pe_ratio = fundamental.get("pe_ratio", 0)
            if pe_ratio > 30:
                risk_score += 15  # High P/E ratio
            
            debt_equity = fundamental.get("debt_to_equity", 0)
            if debt_equity > 1.5:
                risk_score += 25  # High debt levels
            
            # Normalize to 0-100 range
            risk_score = max(0, min(100, risk_score))
            
            return round(risk_score, 1)
            
        except Exception as e:
            return 50.0  # Default risk score

    async def _update_portfolio(self, order: StockOrder):
        """Update portfolio after order execution"""
        try:
            if db is None:
                return

            portfolio_filter = {"user_id": order.user_id, "symbol": order.symbol}
            existing_portfolio = await db.portfolio.find_one(portfolio_filter)
            
            if order.order_type == OrderType.BUY:
                if existing_portfolio:
                    # Update existing position
                    new_quantity = existing_portfolio["quantity"] + order.quantity
                    new_total_invested = existing_portfolio["total_invested"] + order.total_amount
                    new_average_price = new_total_invested / new_quantity
                    
                    await db.portfolio.update_one(
                        portfolio_filter,
                        {
                            "$set": {
                                "quantity": new_quantity,
                                "average_price": new_average_price,
                                "total_invested": new_total_invested,
                                "last_updated": datetime.now(timezone.utc)
                            }
                        }
                    )
                else:
                    # Create new position
                    portfolio = Portfolio(
                        user_id=order.user_id,
                        symbol=order.symbol,
                        quantity=order.quantity,
                        average_price=order.price,
                        total_invested=order.total_amount,
                        current_value=order.total_amount,
                        unrealized_pnl=0,
                        last_updated=datetime.now(timezone.utc)
                    )
                    await db.portfolio.insert_one(portfolio.dict())
            
            elif order.order_type == OrderType.SELL:
                if existing_portfolio and existing_portfolio["quantity"] >= order.quantity:
                    # Update existing position
                    remaining_quantity = existing_portfolio["quantity"] - order.quantity
                    sold_ratio = order.quantity / existing_portfolio["quantity"]
                    sold_investment = existing_portfolio["total_invested"] * sold_ratio
                    
                    if remaining_quantity > 0:
                        # Partial sell
                        new_total_invested = existing_portfolio["total_invested"] - sold_investment
                        new_average_price = new_total_invested / remaining_quantity
                        
                        await db.portfolio.update_one(
                            portfolio_filter,
                            {
                                "$set": {
                                    "quantity": remaining_quantity,
                                    "average_price": new_average_price,
                                    "total_invested": new_total_invested,
                                    "last_updated": datetime.now(timezone.utc)
                                }
                            }
                        )
                    else:
                        # Full sell - remove position
                        await db.portfolio.delete_one(portfolio_filter)

        except Exception as e:
            print(f"Failed to update portfolio: {e}")

# Global instance
stock_service = StockService()
