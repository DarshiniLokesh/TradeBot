import motor.motor_asyncio
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

try:
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
    db = client["tradebot"]
    print(f"Connected to MongoDB at {MONGO_URI}")
except Exception as e:
    print(f"Warning: Could not connect to MongoDB: {e}")
    print("Database operations will be skipped")
    db = None