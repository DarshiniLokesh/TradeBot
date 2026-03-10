import asyncio
import os
import sys
from datetime import datetime, timezone
import motor.motor_asyncio

# Add current directory to path so we can import models if needed
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def simulate(symbol: str):
    # Connect to local MongoDB instance
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
    db = client["tradebot"]
    
    user_id = "default_user"
    symbol = symbol.upper()
    
    print("--- Modifying Database to Simulate Market Drop ---")
    
    # 1. Clear previous test alerts
    await db.user_alerts.delete_many({"user_id": user_id})
    print("Cleared previous alerts.")
    
    # 2. Add an automated plan
    plan = {
        "user_id": user_id,
        "symbol": symbol,
        "quantity": 5,
        "frequency": "daily",
        "created_at": datetime.now(timezone.utc),
        "last_executed": datetime.now(timezone.utc),
        "status": "active"
    }
    await db.automated_plans.insert_one(plan)
    print(f"1. Created an active daily automated plan for 5 shares of {symbol}.")
    
    # 3. Simulate the background automation service detecting a price drop
    print(f"2. Simulating a market drop: Background worker detected {symbol} dropping by 5.2%...")
    alert = {
        "user_id": user_id,
        "symbol": symbol,
        "message": f"🚨 Automated Plan Alert: {symbol} has dropped by -5.20% today. Your automated plan is monitoring this drop. This might be a good time to manually buy the dip!",
        "is_read": False,
        "timestamp": datetime.now(timezone.utc)
    }
    await db.user_alerts.insert_one(alert)
    print("3. Alert successfully generated and saved to database!")
    print("--------------------------------------------------")
    print("You can now go to the chatbot interface and type: 'Show my alerts'")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target_symbol = sys.argv[1]
    else:
        target_symbol = input("Enter a stock symbol to simulate (e.g. AAPL): ")
        
    if not target_symbol:
        target_symbol = "NVDA"
        
    asyncio.run(simulate(target_symbol))
