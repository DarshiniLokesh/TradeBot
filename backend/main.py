from fastapi import FastAPI
from routes import market, trades, users  # match your filenames

app = FastAPI(title="TradeBot API")

app.include_router(market.router)
app.include_router(trades.router)
app.include_router(users.router)

@app.get("/")
async def root():
    return {"message": "API is running"}
