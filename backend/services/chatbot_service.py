import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timezone
from models.stock import StockOrder, OrderType, OrderStatus, AutomatedPlan
from services.stock_service import stock_service
from database import db
import asyncio

class StockChatbotService:
    def __init__(self):
        self.command_patterns = {
            'buy_stock': [
                r'buy\s+(\d+)\s+shares?\s+of\s+([A-Za-z]+)',
                r'buy\s+([A-Za-z]+)\s+(\d+)\s+shares?',
                r'purchase\s+(\d+)\s+([A-Za-z]+)',
                r'buy\s+([A-Za-z]+)\s+at\s+market',
                r'buy\s+(\d+)\s+([A-Za-z]+)\s+at\s+market'
            ],
            'sell_stock': [
                r'sell\s+(\d+)\s+shares?\s+of\s+([A-Za-z]+)',
                r'sell\s+([A-Za-z]+)\s+(\d+)\s+shares?',
                r'sell\s+([A-Za-z]+)\s+at\s+market',
                r'sell\s+(\d+)\s+([A-Za-z]+)\s+at\s+market'
            ],
            'get_price': [
                r'what\s+is\s+the\s+price\s+of\s+([A-Za-z]+)',
                r'price\s+of\s+([A-Za-z]+)',
                r'how\s+much\s+is\s+([A-Za-z]+)',
                r'([A-Za-z]+)\s+stock\s+price',
                r'current\s+price\s+of\s+([A-Za-z]+)'
            ],
            'get_analytics': [
                r'analyze\s+([A-Za-z]+)',
                r'analytics\s+for\s+([A-Za-z]+)',
                r'technical\s+analysis\s+of\s+([A-Za-z]+)',
                r'fundamental\s+analysis\s+of\s+([A-Za-z]+)',
                r'risk\s+assessment\s+of\s+([A-Za-z]+)',
                r'recommendations\s+for\s+([A-Za-z]+)'
            ],
            'get_portfolio': [
                r'show\s+my\s+portfolio',
                r'portfolio\s+summary',
                r'my\s+investments',
                r'current\s+positions',
                r'portfolio\s+status'
            ],
            'get_orders': [
                r'show\s+my\s+orders',
                r'order\s+history',
                r'pending\s+orders',
                r'my\s+trades'
            ],
            'automate_stock': [
                r'automate\s+(\d+)\s+shares?\s+of\s+([A-Za-z]+)',
                r'automate\s+buying\s+(\d+)\s+shares?\s+of\s+([A-Za-z]+)'
            ],
            'get_alerts': [
                r'show\s+my\s+alerts',
                r'price\s+alerts',
                r'my\s+alerts'
            ],
            'best_stock': [
                r'best\s+stock[s]?\s+to\s+buy',
                r'what\s+to\s+buy',
                r'which\s+stock[s]?\s+to\s+buy',
                r'recommend\s+a\s+stock'
            ]
        }
        
        self.help_text = """
🤖 **StockBot Commands**

**Trading Commands:**
• "Buy 10 shares of AAPL" - Purchase stock
• "Sell 5 MSFT" - Sell stock
• "Buy TSLA at market" - Market order

**Information Commands:**
• "What is the price of GOOGL?" - Get current price
• "Analyze AAPL" - Get technical & fundamental analysis
• "Show my portfolio" - View current positions
• "Order history" - View trading history

**Automation & Alerts:**
• "Automate buying 1 share of AAPL" - Setup daily automation plan
• "Show my alerts" - View recent drop alerts

**Examples:**
• "Buy 100 shares of AAPL"
• "Sell 50 MSFT at market"
• "What's the current price of TSLA?"
• "Automate buying 5 shares of MSFT"
• "Show my alerts"
        """

    async def process_message(self, message: str, user_id: str = "default_user") -> str:
        """Process natural language message and return appropriate response"""
        try:
            message = message.strip().lower()
            
            # Check for help command
            if any(word in message for word in ['help', 'commands', 'what can you do']):
                return self.help_text
            
            # Check for greeting
            if any(word in message for word in ['hello', 'hi', 'hey', 'start']):
                return "Hello! I'm StockBot, your AI trading assistant. I can help you buy/sell stocks, get market data, and analyze investments. Type 'help' to see all commands!"
            
            # Process trading commands
            if await self._is_buy_command(message):
                return await self._handle_buy_command(message, user_id)
            
            if await self._is_sell_command(message):
                return await self._handle_sell_command(message, user_id)
            
            if await self._is_automate_command(message):
                return await self._handle_automate_command(message, user_id)
                
            # Process information commands
            if await self._is_best_stock_query(message):
                return await self._handle_best_stock_query()
                
            if await self._is_price_query(message):
                return await self._handle_price_query(message)
            
            if await self._is_analytics_query(message):
                return await self._handle_analytics_query(message)
            
            if await self._is_portfolio_query(message):
                return await self._handle_portfolio_query(user_id)
            
            if await self._is_orders_query(message):
                return await self._handle_orders_query(user_id)
                
            if await self._is_alerts_query(message):
                return await self._handle_alerts_query(user_id)
            
            # Default response
            return "I didn't understand that command. Try saying 'help' to see what I can do, or ask me to buy/sell stocks, get prices, or analyze investments."
            
        except Exception as e:
            return f"Sorry, I encountered an error: {str(e)}. Please try again."

    async def _is_buy_command(self, message: str) -> bool:
        """Check if message is a buy command"""
        for pattern in self.command_patterns['buy_stock']:
            if re.search(pattern, message):
                return True
        return False

    async def _is_sell_command(self, message: str) -> bool:
        """Check if message is a sell command"""
        # Check for explicit sell patterns
        for pattern in self.command_patterns['sell_stock']:
            if re.search(pattern, message):
                return True
        
        # Check for sell-related keywords
        sell_keywords = ['sell', 'sell off', 'liquidate', 'exit position']
        if any(keyword in message.lower() for keyword in sell_keywords):
            # Make sure it's not asking about selling (like "what if I sell")
            if not any(word in message.lower() for word in ['what if', 'what would', 'how much', 'when']):
                return True
        
        return False

    async def _is_price_query(self, message: str) -> bool:
        """Check if message is asking for price"""
        for pattern in self.command_patterns['get_price']:
            if re.search(pattern, message):
                return True
        return False

    async def _is_analytics_query(self, message: str) -> bool:
        """Check if message is asking for analytics"""
        for pattern in self.command_patterns['get_analytics']:
            if re.search(pattern, message):
                return True
        return False

    async def _is_portfolio_query(self, message: str) -> bool:
        """Check if message is asking for portfolio"""
        for pattern in self.command_patterns['get_portfolio']:
            if re.search(pattern, message):
                return True
        return False

    async def _is_orders_query(self, message: str) -> bool:
        """Check if message is asking for orders"""
        for pattern in self.command_patterns['get_orders']:
            if re.search(pattern, message):
                return True
        return False

    async def _is_automate_command(self, message: str) -> bool:
        """Check if message is an automate command"""
        for pattern in self.command_patterns['automate_stock']:
            if re.search(pattern, message):
                return True
        # Additional keyword check
        if 'automate' in message and 'buy' in message:
            return True
        return False

    async def _is_alerts_query(self, message: str) -> bool:
        """Check if message is asking for alerts"""
        for pattern in self.command_patterns['get_alerts']:
            if re.search(pattern, message):
                return True
        return False
        
    async def _is_best_stock_query(self, message: str) -> bool:
        """Check if message is asking for best stock recommendations"""
        for pattern in self.command_patterns['best_stock']:
            if re.search(pattern, message):
                return True
        return False

    async def _handle_buy_command(self, message: str, user_id: str) -> str:
        """Handle buy stock commands"""
        try:
            # Extract quantity and symbol
            quantity, symbol = self._extract_quantity_and_symbol(message, 'buy')
            
            if not quantity or not symbol:
                return "Please specify the quantity and stock symbol. Example: 'Buy 10 shares of AAPL'"
            
            # Analyze ordered stock
            try:
                analytics = await stock_service.get_stock_analytics(symbol)
                risk_level = "🟢 Low" if analytics.risk_score < 30 else "🟡 Medium" if analytics.risk_score < 70 else "🔴 High"
                analysis_msg = f"📊 **Quick Analysis:** Risk Level is {risk_level} ({analytics.risk_score}/100). {analytics.recommendations[0] if analytics.recommendations else ''}"
            except Exception:
                analysis_msg = "Could not analyze the requested stock."
                
            # Suggest best stock
            try:
                best_opportunity = await stock_service.get_best_market_opportunity()
                if best_opportunity["symbol"] != symbol.upper():
                    suggestion_msg = f"\n\n💡 **Market Suggestion:** Given the current market situation, you might also consider **{best_opportunity['symbol']}** (Price: ${best_opportunity['price']:.2f}). It has a low risk score ({best_opportunity['risk_score']}) and the analysis shows: {best_opportunity['recommendation'].lower()}"
                else:
                    suggestion_msg = f"\n\n💡 **Great Choice!** {symbol.upper()} is currently our top recommended stock to buy."
            except Exception:
                suggestion_msg = ""
            
            return f"""
🛑 **Order Not Placed automatically**

I've analyzed your request to buy {quantity} shares of {symbol.upper()}:

{analysis_msg}{suggestion_msg}

If you still want to proceed with buying {symbol.upper()}, please use the trading interface to manually confirm your order.
""".strip()

            
        except Exception as e:
            return f"❌ Failed to process buy command: {str(e)}"

    async def _handle_best_stock_query(self) -> str:
        """Handle request for the best stock to buy right now"""
        try:
            # We already have a function that finds the best stock based on lowest risk score
            best_opportunity = await stock_service.get_best_market_opportunity()
            
            # Find a bad stock (highest risk score) as a "what not to buy" suggestion
            popular_symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA"]
            worst_stock = None
            highest_risk = 0
            worst_analytics = None
            
            # Since get_best_market_opportunity already does similar, we could optimize, 
            # but for simplicity we fetch sequentially or concurrently here
            tasks = [stock_service.get_stock_analytics(sym) for sym in popular_symbols]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    continue
                if result.risk_score > highest_risk:
                    highest_risk = result.risk_score
                    worst_stock = popular_symbols[i]
                    worst_analytics = result
                    
            if not worst_stock:
                worst_stock = "Unknown"
                highest_risk = 100
                worst_reason = "No data available"
            else:
                worst_reason = worst_analytics.recommendations[0] if worst_analytics.recommendations else "High risk based on current indicators."

            response = f"""
📈 **Market Recommendations Based on Real-Time Data**

✅ **Best Stock to Buy:** **{best_opportunity['symbol']}**
• **Current Price:** ${best_opportunity['price']:.2f}
• **Risk Score:** 🟢 Low ({best_opportunity['risk_score']}/100)
• **Analysis:** {best_opportunity['recommendation']}

❌ **Stock to Avoid Right Now:** **{worst_stock}**
• **Risk Score:** 🔴 High ({highest_risk}/100)
• **Analysis:** {worst_reason}

*Note: This is based on technical and fundamental indicators. Always do your own research before investing.*
""".strip()
            return response
        except Exception as e:
            return f"❌ Failed to get stock recommendations: {str(e)}"

    async def _handle_sell_command(self, message: str, user_id: str) -> str:
        """Handle sell stock commands"""
        try:
            # Extract quantity and symbol
            quantity, symbol = self._extract_quantity_and_symbol(message, 'sell')
            
            if not quantity or not symbol:
                return "Please specify the quantity and stock symbol. Example: 'Sell 5 shares of MSFT'"
            
            # Get current market price
            stock_data = await stock_service.get_stock_data(symbol)
            
            # Create order
            order = StockOrder(
                symbol=symbol.upper(),
                order_type=OrderType.SELL,
                quantity=quantity,
                price=stock_data.price,
                total_amount=quantity * stock_data.price,
                user_id=user_id,
                notes="Order placed via chatbot"
            )
            
            # Set order status to EXECUTED so portfolio updates immediately
            order.status = OrderStatus.EXECUTED
            
            # Place order (which will update portfolio since status is EXECUTED)
            placed_order = await stock_service.place_order(order)
            
            return f"""
✅ **Sell Order Executed Successfully!**

**Stock:** {symbol.upper()}
**Quantity:** {quantity} shares
**Price:** ${stock_data.price:.2f}
**Total Amount:** ${placed_order.total_amount:.2f}
**Order ID:** {placed_order.id}

Your order has been executed and portfolio updated!
            """.strip()
            
        except Exception as e:
            return f"❌ Failed to place sell order: {str(e)}"

    async def _handle_price_query(self, message: str) -> str:
        """Handle price queries"""
        try:
            # Extract symbol
            symbol = self._extract_symbol(message)
            
            if not symbol:
                return "Please specify a stock symbol. Example: 'What is the price of AAPL?'"
            
            # Get stock data
            stock_data = await stock_service.get_stock_data(symbol)
            
            # Format response
            change_emoji = "📈" if stock_data.change >= 0 else "📉"
            change_color = "🟢" if stock_data.change >= 0 else "🔴"
            
            return f"""
{change_emoji} **{symbol.upper()} Stock Price**

**Current Price:** ${stock_data.price:.2f}
**Change:** {change_color} ${stock_data.change:.2f} ({stock_data.change_percent:.2f}%)
**Volume:** {stock_data.volume:,}
**Market Cap:** ${stock_data.market_cap/1e9:.2f}B (if available)
**P/E Ratio:** {stock_data.pe_ratio:.2f} (if available)

**Trading Range:**
• Open: ${stock_data.open_price:.2f}
• High: ${stock_data.high_price:.2f}
• Low: ${stock_data.low_price:.2f}
            """.strip()
            
        except Exception as e:
            return f"❌ Failed to get price: {str(e)}"

    async def _handle_analytics_query(self, message: str) -> str:
        """Handle analytics queries"""
        try:
            # Extract symbol
            symbol = self._extract_symbol(message)
            
            if not symbol:
                return "Please specify a stock symbol. Example: 'Analyze AAPL'"
            
            # Get analytics
            analytics = await stock_service.get_stock_analytics(symbol)
            
            # Format response
            risk_level = "🟢 Low" if analytics.risk_score < 30 else "🟡 Medium" if analytics.risk_score < 70 else "🔴 High"
            
            response = f"""
📊 **{symbol.upper()} Analytics Report**

**Risk Score:** {risk_level} ({analytics.risk_score}/100)

**Technical Indicators:**
• RSI: {analytics.technical_indicators.get('rsi', 0):.2f}
• MACD: {analytics.technical_indicators.get('macd', 0):.2f}
• 20-day SMA: ${analytics.technical_indicators.get('sma_20', 0):.2f}
• 50-day SMA: ${analytics.technical_indicators.get('sma_50', 0):.2f}

**Fundamental Metrics:**
• P/E Ratio: {analytics.fundamental_metrics.get('pe_ratio', 'N/A')}
• Market Cap: ${analytics.fundamental_metrics.get('market_cap', 0)/1e9:.2f}B (if available)
• Debt/Equity: {analytics.fundamental_metrics.get('debt_to_equity', 'N/A')}

**Recommendations:**
"""
            
            for rec in analytics.recommendations:
                response += f"• {rec}\n"
            
            response += f"\n**Last Updated:** {analytics.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
            
            return response.strip()
            
        except Exception as e:
            return f"❌ Failed to get analytics: {str(e)}"

    async def _handle_portfolio_query(self, user_id: str) -> str:
        """Handle portfolio queries"""
        try:
            # Get portfolio
            portfolios = await stock_service.get_portfolio(user_id)
            
            if not portfolios:
                return "📭 You don't have any positions in your portfolio yet. Start by buying some stocks!"
            
            # Calculate totals
            total_invested = sum(p.total_invested for p in portfolios)
            total_current = sum(p.current_value for p in portfolios)
            total_pnl = sum(p.unrealized_pnl for p in portfolios)
            overall_return = (total_pnl / total_invested * 100) if total_invested > 0 else 0
            
            response = f"""
💼 **Portfolio Summary**

**Total Positions:** {len(portfolios)}
**Total Invested:** ${total_invested:.2f}
**Current Value:** ${total_current:.2f}
**Unrealized P&L:** {'🟢' if total_pnl >= 0 else '🔴'} ${total_pnl:.2f} ({overall_return:.2f}%)

**Positions:**
"""
            
            for portfolio in portfolios:
                pnl_emoji = "🟢" if portfolio.unrealized_pnl >= 0 else "🔴"
                response += f"""
**{portfolio.symbol}:**
• Quantity: {portfolio.quantity} shares
• Avg Price: ${portfolio.average_price:.2f}
• Current Value: ${portfolio.current_value:.2f}
• P&L: {pnl_emoji} ${portfolio.unrealized_pnl:.2f}
"""
            
            return response.strip()
            
        except Exception as e:
            return f"❌ Failed to get portfolio: {str(e)}"

    async def _handle_orders_query(self, user_id: str) -> str:
        """Handle orders queries"""
        try:
            # This would require additional database queries for orders
            # For now, return a placeholder
            return """
📋 **Order History**

This feature is coming soon! I'll be able to show you:
• Pending orders
• Executed trades
• Order status updates
• Trade history

For now, you can place new orders using commands like:
• "Buy 10 shares of AAPL"
• "Sell 5 MSFT"
            """.strip()
            
        except Exception as e:
            return f"❌ Failed to get orders: {str(e)}"

    async def _handle_automate_command(self, message: str, user_id: str) -> str:
        """Handle automate buy stock commands"""
        try:
            # Clean up message to make parsing easier by converting it to a standard 'buy' command format
            clean_message = message.replace("automate buying", "buy").replace("automate", "buy")
            quantity, symbol = self._extract_quantity_and_symbol(clean_message, "buy")
            
            if not quantity or not symbol:
                return "Please specify the quantity and stock symbol for automation. Example: 'Automate buying 10 shares of AAPL'"
            
            symbol = symbol.upper()
            
            # Check if stock exists
            await stock_service.get_stock_data(symbol)
            
            plan = AutomatedPlan(
                user_id=user_id,
                symbol=symbol,
                quantity=quantity,
                frequency="daily",
                created_at=datetime.now(timezone.utc)
            )
            
            result = await db.automated_plans.insert_one(plan.dict())
            
            return f"""
🤖 **Automated Trading Plan Activated!**

**Stock:** {symbol}
**Quantity:** {quantity} shares
**Frequency:** Daily

I will execute a buy order for {quantity} shares of {symbol} every day. I will also monitor {symbol} and alert you if the price drops by 2% or more.
""".strip()
        except Exception as e:
            return f"❌ Failed to setup automation: {str(e)}"

    async def _handle_alerts_query(self, user_id: str) -> str:
        """Handle alerts query"""
        try:
            if db is None:
                return "Database not available"
                
            cursor = db.user_alerts.find({"user_id": user_id}).sort("timestamp", -1).limit(5)
            alerts = await cursor.to_list(length=5)
            
            if not alerts:
                return "📭 You have no recent price drop alerts."
                
            response = "🔔 **Recent Alerts:**\n\n"
            for alert in alerts:
                # Format time string correctly without modifying dictionary inline
                tz_aware_time = alert['timestamp']
                if tz_aware_time.tzinfo is None:
                    tz_aware_time = tz_aware_time.replace(tzinfo=timezone.utc)
                time_str = tz_aware_time.strftime('%b %d, %H:%M')
                response += f"• [{time_str}] {alert['message']}\n\n"
                
            return response.strip()
        except Exception as e:
            return f"❌ Failed to get alerts: {str(e)}"

    def _extract_quantity_and_symbol(self, message: str, action: str) -> Tuple[Optional[int], Optional[str]]:
        """Extract quantity and symbol from buy/sell commands"""
        try:
            # Try different patterns
            patterns = [
                rf'{action}\s+(\d+)\s+shares?\s+of\s+([A-Za-z]+)',
                rf'{action}\s+([A-Za-z]+)\s+(\d+)\s+shares?',
                rf'{action}\s+(\d+)\s+([A-Za-z]+)',
                rf'{action}\s+([A-Za-z]+)\s+at\s+market'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, message)
                if match:
                    if 'at market' in message:
                        # For market orders, assume 1 share if quantity not specified
                        return 1, match.group(1)
                    else:
                        groups = match.groups()
                        if len(groups) == 2:
                            # Check which group is quantity vs symbol
                            if groups[0].isdigit():
                                return int(groups[0]), groups[1]
                            else:
                                return int(groups[1]), groups[0]
            
            return None, None
            
        except Exception:
            return None, None

    def _extract_symbol(self, message: str) -> Optional[str]:
        """Extract stock symbol from message"""
        try:
            # Look for symbols after "of" or "for" (most common pattern)
            of_pattern = r'(?:of|for)\s+([A-Za-z]{3,5})'
            match = re.search(of_pattern, message, re.IGNORECASE)
            if match:
                return match.group(1).upper()
            
            # Look for symbols in quotes
            quoted_pattern = r'"([A-Za-z]{3,5})"'
            match = re.search(quoted_pattern, message)
            if match:
                return match.group(1).upper()
            
            # Look for common stock symbols (3-5 letters) at word boundaries
            symbol_pattern = r'\b([A-Z]{3,5})\b'
            matches = re.findall(symbol_pattern, message.upper())
            
            if matches:
                # Filter out common words that aren't stock symbols
                common_words = {'THE', 'AND', 'FOR', 'ARE', 'YOU', 'CAN', 'GET', 'BUY', 'SELL', 'SHOW', 'WHAT', 'WHEN', 'WHERE', 'WHY', 'HOW'}
                valid_symbols = [s for s in matches if s not in common_words]
                if valid_symbols:
                    return valid_symbols[0]
            
            return None
            
        except Exception:
            return None

# Global instance
chatbot_service = StockChatbotService()
