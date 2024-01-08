import asyncio
import os
import datetime
import time

from binance.um_futures import UMFutures
from dotenv import load_dotenv, find_dotenv
from app.bot.headers import headers
from requests.exceptions import ConnectionError

import aiohttp

load_dotenv(find_dotenv())



class Trade:
    def __init__(self, api_key: str, api_secret: str):
        self.symbols = []
        self.apikey = api_key
        self.api_secret = api_secret

        self.um_futures_client = UMFutures(
            key=self.apikey,
            secret=self.api_secret
        )

    async def get_all_futures_symbols(self):
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get('https://www.binance.com/fapi/v1/exchangeInfo?showall=false') as response:
                result = await response.json()

                for results in result['symbols']:
                    self.symbols.append(results['symbol'])

        return self.symbols

    async def get_price(self, symbol: str):
        price = self.um_futures_client.ticker_price(symbol)
        return price['price']

    async def into_order(self, symbol: str, quantity: int):
        params = {
            'symbol': symbol,
            'side': 'BUY',
            'type': 'MARKET',
            'quantity': int(quantity),
            'recvWindow': 6000
        }
        self.um_futures_client.new_order(**params)

    async def stop_loss(self, symbol):
        get_price = await Trade.get_price(self, symbol=symbol)
        price = -(float(get_price) * 0.2 / 100) + float(get_price)
        params = {
            'symbol': symbol,
            'side': 'SELL',
            'type': 'STOP_MARKET',
            'stopPrice': float(round(price, 4)),
            'closePosition': 'True'
        }
        self.um_futures_client.new_order(**params)

    async def take_profit(self, symbol):
        get_price = await Trade.get_price(self, symbol=symbol)
        price = (float(get_price) * 0.7 / 100) + float(get_price)

        params = {
            'symbol': symbol,
            'side': 'SELL',
            'type': 'TAKE_PROFIT_MARKET',
            'stopPrice': float(round(price, 4)),
            'closePosition': 'True'
        }
        self.um_futures_client.new_order(**params)

    async def get_kline_1m(self, balance: float):
        print('Запустилась')
        try:
            keep_running = True

            while keep_running is True:
                now = datetime.datetime.now()
                second = now.second
                if int(second) == 1:

                    data = await Trade.get_all_futures_symbols(self)

                    for symbol in data[0:145]:
                        if 'USDT' in symbol:

                            try:
                                kline = self.um_futures_client.klines(
                                    symbol=f'{symbol}',
                                    interval='1m',
                                    limit=1,
                                    recvWindow=6000
                                )

                                for klines in kline:
                                    my_deposit = balance / float(klines[4])

                                    if float(klines[4]) > float(my_deposit):
                                        continue
                                    if klines[1] < klines[4]:
                                        time.sleep(2)
                                        num = ((float(klines[4]) - float(klines[1])) / float(klines[1])) * 100
                                        if float(num) >= 2.2:
                                            print('Зашла в сделку')

                                            print(symbol)
                                            await Trade.into_order(self, symbol=symbol, quantity=int(my_deposit))
                                            await Trade.stop_loss(self, symbol=symbol)
                                            await Trade.take_profit(self, symbol=symbol)
                                            keep_running = False
                                            break
                            except KeyError:
                                continue

                        if keep_running is False:
                            time.sleep(600)
                            await Trade.get_kline_1m(self, balance)

        except ConnectionError:
            await Trade.get_kline_1m(self, balance)
