from fastapi import APIRouter

router = APIRouter(prefix="/trades", tags=["Trades"])

@router.get("/")
async def get_trades():
    return {"message": "Trades route working"}
