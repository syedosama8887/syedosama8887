from fastapi import FastAPI, HTTPException, Body, BackgroundTasks
import os
from dotenv import load_dotenv
from services import BybitAPI
# FastAPI app setup
app = FastAPI()
# Load environment variables
load_dotenv()
api_key = os.getenv('API_KEY')
api_secret = os.getenv('SECRET_KEY')
bybit_api = BybitAPI(api_key, api_secret)

@app.get("/balance")
async def read_balance():
    try:
        balance = bybit_api.fetch_balance()
        return balance
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.get("/markets")
async def read_markets():
    try:
        markets = bybit_api.fetch_market_symbols()
        return markets
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.post("/create-limit-order")
async def create_limit_order(symbol: str = Body(...), order_type: str = Body(...), amount: float = Body(...), price: float = Body(...)):
    try:
        order = bybit_api.create_limit_order(symbol, order_type, amount/price, price)
        return order
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.post("/start-grid-bot")
async def start_grid_bot(background_tasks: BackgroundTasks, starting_point: float = Body(...), symbol: str = Body(...), interval: float = Body(...), buy_amount: float = Body(...), sell_amount: float = Body(...), simultaneousOrders: int = Body(...)):
    try:
        background_tasks.add_task(bybit_api.monitor_price, symbol, starting_point, interval, buy_amount, sell_amount, simultaneousOrders)
        return {"message": "Grid bot started"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.post("/stop-grid-bot")
async def stop_grid_bot():
    bybit_api.stop_grid_bot()
    return {"message": "Grid bot stopped"}
# Run the server using Uvicorn programmatically (for debugging)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)