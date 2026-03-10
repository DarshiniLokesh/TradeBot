import asyncio
from datetime import datetime, timezone, timedelta
from database import db
from services.stock_service import stock_service
from models.stock import StockOrder, OrderType, OrderStatus, UserAlert
from bson import ObjectId

class AutomationService:
    def __init__(self):
        self.is_running = False

    async def start(self):
        """Start the background automation task"""
        if self.is_running:
            return
        self.is_running = True
        print("Starting Automation Service...")
        
        while self.is_running:
            try:
                await self.process_all_plans()
            except Exception as e:
                print(f"Error in automation service loop: {e}")
            
            # For demonstration, check every 60 seconds
            # In production, you might configure this differently.
            await asyncio.sleep(60)

    def stop(self):
        self.is_running = False

    async def process_all_plans(self):
        """Iterate over all active automated plans and execute logic"""
        if db is None:
            return
            
        now = datetime.now(timezone.utc)
        
        cursor = db.automated_plans.find({"status": "active"})
        plans = await cursor.to_list(length=None)
        
        for plan_doc in plans:
            try:
                symbol = plan_doc["symbol"]
                user_id = plan_doc["user_id"]
                quantity = plan_doc["quantity"]
                last_executed = plan_doc.get("last_executed")
                last_alert = plan_doc.get("last_alert_time")
                
                # Ensure last_executed and last_alert are datetime and timezone aware
                if last_executed and last_executed.tzinfo is None:
                    last_executed = last_executed.replace(tzinfo=timezone.utc)
                if last_alert and last_alert.tzinfo is None:
                    last_alert = last_alert.replace(tzinfo=timezone.utc)
                
                # Fetch stock data
                stock_data = await stock_service.get_stock_data(symbol)
                
                # 1. Execute Daily Order
                # We do this if 'last_executed' is None, or it was > 24 hours ago
                if last_executed is None or (now - last_executed).total_seconds() > 86400:
                    print(f"Executing daily plan for {user_id}: Buying {quantity} {symbol}")
                    order = StockOrder(
                        symbol=symbol.upper(),
                        order_type=OrderType.BUY,
                        quantity=quantity,
                        price=stock_data.price,
                        total_amount=quantity * stock_data.price,
                        user_id=user_id,
                        notes="Automated Daily Order"
                    )
                    order.status = OrderStatus.EXECUTED
                    placed_order = await stock_service.place_order(order)
                    
                    # Update plan
                    await db.automated_plans.update_one(
                        {"_id": plan_doc["_id"]},
                        {"$set": {"last_executed": now}}
                    )
                
                # 2. Check for drop alerts
                # If change percent is lower than -2%, and we haven't alerted in the last 12 hours
                if stock_data.change_percent < -2.0:
                    if last_alert is None or (now - last_alert).total_seconds() > 43200: # 12 hours
                        print(f"Sending low price alert for {symbol} to {user_id}")
                        alert = UserAlert(
                            user_id=user_id,
                            symbol=symbol,
                            message=f"🔔 Alert: {symbol} has dropped by {stock_data.change_percent:.2f}%. Current price is ${stock_data.price:.2f}. This might be a good time to buy more, or review your automated plan.",
                            timestamp=now
                        )
                        await db.user_alerts.insert_one(alert.dict())
                        
                        await db.automated_plans.update_one(
                            {"_id": plan_doc["_id"]},
                            {"$set": {"last_alert_time": now}}
                        )
                        
            except Exception as e:
                print(f"Error processing plan for {plan_doc.get('symbol')}: {e}")

# Global instance
automation_service = AutomationService()
