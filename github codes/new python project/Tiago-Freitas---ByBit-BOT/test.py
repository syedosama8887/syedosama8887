import os
from dotenv import load_dotenv
from services import BybitAPI

load_dotenv()
api_key = os.getenv("API_KEY")
api_secret = os.getenv("SECRET_KEY")
bybit_api = BybitAPI(api_key, api_secret)



open_orders =  bybit_api.monitor_price("BTC/USDT", 40000, 100, 6, 3)

