import ccxt
import asyncio
from fastapi import BackgroundTasks
# Your BybitAPI class

class BybitAPI:
    def __init__(self, api_key: str, api_secret: str):
        self.exchange = ccxt.bybit({
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True
        })
        self.exchange.setSandboxMode(True)
        self.botSwitch = False
        # Initialize current buy and sell prices
        self.current_buy_price = None
        self.current_sell_price = None

        # Initialize buy and sell prices
        self.buy_orders = []
        self.sell_order = None
    def fetch_balance(self):
        if not self.exchange.has['fetchBalance']:
            raise Exception('The exchange does not support fetchBalance')
        return self.exchange.fetch_balance()

    def fetch_market_symbols(self):
        markets = self.exchange.load_markets()
        return list(markets.keys())  # Extracts and returns only the symbols
    def create_limit_order(self, symbol, order_type, amount, price):
        try:
            # 'order_type' should be 'buy' or 'sell'
            order = self.exchange.create_limit_order(symbol, order_type, amount, price)
            return order
        except Exception as e:
            raise e
    def fetch_current_price(self, symbol):
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return ticker['last']  # 'last' price is the most recent market price
        except Exception as e:
            raise e
    def convert_usd_to_crypto(self, symbol, usd_amount):
        try:
            current_price = self.fetch_current_price(symbol)
            return usd_amount / current_price
        except Exception as e:
            raise e
    def fetch_open_limit_orders(self, symbol=None):
        all_orders = []
        cursor = None  # Initial cursor is None
        try:
            while True:
                params = {'limit': 50}
                if cursor:
                    params['cursor'] = cursor  # Add cursor to params if it exists

                orders = self.exchange.fetch_open_orders(symbol, params=params)

                if not orders:
                    break  # No more orders to fetch

                all_orders.extend(orders)
                print(f"Fetched {len(orders)} orders, total: {len(all_orders)}")

                # Extract nextPageCursor from the last order's info field
                nextPageCursor = orders[-1]['info'].get('nextPageCursor')
                if nextPageCursor:
                    cursor = nextPageCursor  # Assuming cursor needs to be split and only the first part is used
                else:
                    break  # No cursor for the next page

            return all_orders

        except Exception as e:
            print(f"Error in fetch_open_limit_orders: {e}")
            return []

    def cancel_all_limit_orders(self, symbol=None):
        try:
            open_orders = self.fetch_open_limit_orders(symbol)
            for order in open_orders:
                self.exchange.cancel_order(order['id'], order['symbol'])
            return f"All open limit orders for {symbol} have been cancelled."
        except Exception as e:
            raise e

    async def monitor_price(self, symbol, starting_point, interval, buy_amount, sell_amount, simultaneousOrders = 50):
        # Initial setup for buy and sell orders
        self.buy_orders = []
        current_price = starting_point + interval
        while current_price > 0:
            self.buy_orders.append(current_price)
            current_price -= interval
        print(self.buy_orders)
        # Place initial orders
        for price in self.buy_orders[1:simultaneousOrders+1]:
            self.create_limit_order(symbol, 'buy', buy_amount/price, price)
        await asyncio.sleep(5)
        # Fetch current open orders
        open_orders = self.fetch_open_limit_orders(symbol)
        open_buy_prices = [order['price'] for order in open_orders if order['side'] == 'buy']
        open_sell_prices = [order['price'] for order in open_orders if order['side'] == 'sell']
        new_buy_orders = self.buy_orders[self.buy_orders.index(max(open_buy_prices)):self.buy_orders.index(max(open_buy_prices))+simultaneousOrders]
        new_sell_orders = self.buy_orders[0:self.buy_orders.index(max(open_buy_prices))-1] if not new_buy_orders[0]==starting_point else []
        # Place new buy orders avoiding duplicates
        for price in new_buy_orders:
            if price not in open_buy_prices:
                self.create_limit_order(symbol, 'buy', buy_amount / price, price)

        print(len(open_orders))
        # Place new sell orders avoiding duplicates
        for price in new_sell_orders:
            if price not in open_sell_prices:
                self.create_limit_order(symbol, 'sell', sell_amount / price, price)
        while True:
            try:# The commented code block is responsible for fetching the current open orders,
            # determining the new buy and sell orders to be placed, and placing those orders while
            # avoiding duplicates.
                print('something')
                # Fetch current open orders
                open_orders = self.fetch_open_limit_orders(symbol)
                open_buy_prices = [order['price'] for order in open_orders if order['side'] == 'buy']
                open_sell_prices = [order['price'] for order in open_orders if order['side'] == 'sell']
                new_buy_orders = self.buy_orders[self.buy_orders.index(max(open_buy_prices)):self.buy_orders.index(max(open_buy_prices))+simultaneousOrders]
                new_sell_orders = self.buy_orders[0:self.buy_orders.index(max(open_buy_prices))-1] if not new_buy_orders[0]==starting_point else []
                print(new_sell_orders, open_sell_prices)
                print(new_buy_orders, open_buy_prices)
                # Place new buy orders avoiding duplicates
                for price in new_buy_orders:
                    if price not in open_buy_prices:
                        print(f'Buy at: {price}')
                        self.create_limit_order(symbol, 'buy', buy_amount / price, price)

                # Place new sell orders avoiding duplicates
                for price in new_sell_orders:
                    if price not in open_sell_prices:
                        print(f'Sell at: {price}')
                        self.create_limit_order(symbol, 'sell', sell_amount / price, price)
                await asyncio.sleep(5)
            except Exception as e:
                print(f"Error in Bot: {e}")
                await asyncio.sleep(1)

    def start_grid_bot(self, background_tasks: BackgroundTasks, symbol: str, interval: float):
        self.botSwitch = True
        background_tasks.add_task(self.monitor_price, symbol, interval)

    def stop_grid_bot(self):
        self.botSwitch = False