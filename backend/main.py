from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from routes import market, trades, users  # match your filenames
from services.automation_service import automation_service

app = FastAPI(title="TradeBot API")

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(automation_service.start())

# Configure CORS to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://trade-bot-gamma.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(market.router)
app.include_router(trades.router)
app.include_router(users.router)

@app.get("/")
async def root():
    return {"message": "API is running"}
