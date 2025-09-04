import aiohttp
import asyncio
from datetime import datetime, date, timedelta
# from _util import _to_milliseconds
from ._util import _to_milliseconds
import pandas as pd

class BinanceSwap:
    def __init__(self) -> None:
        self.session = aiohttp.ClientSession()

    async def get_klines(self, symbol: str, interval: str, start_time, end_time = None, limit: int = 1500):
        """
        获取U本位合约K线数据，支持获取任意长度（自动分批）

        :param symbol: 交易对, 如 'BTCUSDT'
        :param interval: K线间隔, 如 '1m', '5m', '1h', '1d'
        :param start_time: 开始时间, 毫秒时间戳或datetime/date类型
        :param end_time: 结束时间, 毫秒时间戳或datetime/date类型, 默认为None表示最新
        :param limit: 每次请求最大K线数量, 最大1500
        :return: K线数据DataFrame
        """
        url = "https://fapi.binance.com/fapi/v1/klines"
        all_klines = []
        fetch_start = _to_milliseconds(start_time)
        ms_end_time = _to_milliseconds(end_time) if end_time else None
        while True:
            params = {
                "symbol": symbol.upper(),
                "interval": interval,
                "startTime": fetch_start,
                "limit": limit
            }
            if ms_end_time:
                params["endTime"] = ms_end_time
            async with self.session.get(url, params=params) as resp:
                resp.raise_for_status()
                data = await resp.json()
                if not data:
                    break
                all_klines.extend(data)
                if len(data) < limit:
                    break
                last_open_time = data[-1][0]
                fetch_start = last_open_time + 1
                if ms_end_time and fetch_start >= ms_end_time:
                    break
        # 转为DataFrame
        columns = [
            "open_time", "open", "high", "low", "close", "volume",
            "close_time", "quote_asset_volume", "number_of_trades",
            "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume", "ignore"
        ]
        df = pd.DataFrame(all_klines, columns=columns)
        # 类型转换
        df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")
        df["close_time"] = pd.to_datetime(df["close_time"], unit="ms")
        for col in ["open", "high", "low", "close", "volume", "quote_asset_volume", "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        df["number_of_trades"] = df["number_of_trades"].astype(int)
        return df

    async def get_index_klines(self, pair: str, interval: str, start_time, end_time=None, limit: int = 1500):
        """
        获取U本位合约指数K线数据，支持获取任意长度（自动分批）

        :param pair: 指数对, 如 'BTCUSDT'
        :param interval: K线间隔, 如 '1m', '5m', '1h', '1d'
        :param start_time: 开始时间, 毫秒时间戳或datetime/date类型
        :param end_time: 结束时间, 毫秒时间戳或datetime/date类型, 默认为None表示最新
        :param limit: 每次请求最大K线数量, 最大1500
        :return: 指数K线数据DataFrame
        """
        url = "https://fapi.binance.com/fapi/v1/indexPriceKlines"
        all_klines = []
        fetch_start = _to_milliseconds(start_time)
        ms_end_time = _to_milliseconds(end_time) if end_time else None
        while True:
            params = {
                "pair": pair.upper(),
                "interval": interval,
                "startTime": fetch_start,
                "limit": limit
            }
            if ms_end_time:
                params["endTime"] = ms_end_time
            async with self.session.get(url, params=params) as resp:
                resp.raise_for_status()
                data = await resp.json()
                if not data:
                    break
                all_klines.extend(data)
                if len(data) < limit:
                    break
                last_open_time = data[-1][0]
                fetch_start = last_open_time + 1
                if ms_end_time and fetch_start >= ms_end_time:
                    break
        columns = [
            "open_time", "open", "high", "low", "close", "volume",
            "close_time", "quote_asset_volume", "number_of_trades",
            "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume", "ignore"
        ]
        df = pd.DataFrame(all_klines, columns=columns)
        df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")
        df["close_time"] = pd.to_datetime(df["close_time"], unit="ms")
        for col in ["open", "high", "low", "close", "volume", "quote_asset_volume", "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        df["number_of_trades"] = df["number_of_trades"].astype(int)
        return df

