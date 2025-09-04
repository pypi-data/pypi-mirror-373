import aiohttp
import asyncio
import pandas as pd
import time
from datetime import datetime, timezone
from ._util import _to_milliseconds  # 确保时间转换函数可用

class OKX:
    def __init__(self) -> None:
        self.session = aiohttp.ClientSession()
        self.base_url = "https://www.okx.com/api/v5/market"

    async def get_klines(self, symbol: str, interval: str, start_time, end_time=None, limit: int = 100):
        """
        获取 OKX 永续合约 K 线数据，带时间过滤，从 end_time 向 start_time 方向翻页。

        :param symbol: 交易对, 如 'BTC-USDT'
        :param interval: K 线间隔, 如 '1m', '15m', '1H', '4H', '1D'
        :param start_time: 开始时间(datetime 或 毫秒)
        :param end_time: 结束时间(datetime 或 毫秒), 可选
        :param limit: 每次请求最大数量(OKX 最大 300)
        :return: DataFrame 格式的 K 线数据，按时间升序
        """
        if 'h' in interval or 'd' in interval:
            interval = interval.upper()  # 确保间隔是大写格式

        url = f"{self.base_url}/history-candles"
        all_rows = []
        # 转换 start_time 和 end_time 到毫秒时间戳
        if isinstance(start_time, (int, float)):
            start_ts = int(start_time)
        else:
            # 处理 datetime 对象
            start_ts = int(start_time.timestamp() * 1000)
        if end_time:
            if isinstance(end_time, (int, float)):
                end_ts = int(end_time)
            else:
                end_ts = int(end_time.timestamp() * 1000)
        else:
            # 如果没有指定结束时间，就用当前时间戳
            end_ts = int(time.time() * 1000)

        # 每次请求最多返回 limit=300
        batch_limit = min(limit, 300)
        # 初始 after 参数为 end_ts，向过去翻页
        current_after = end_ts

        while True:
            params = {
                "instId": symbol,
                "bar": interval,
                "limit": str(batch_limit),
                "after": str(current_after)
            }
            # 发送请求
            async with self.session.get(url, params=params) as resp:
                data = await resp.json()
                if not data or data.get("code") != "0" or not data.get("data"):
                    # 返回错误或无数据，结束循环
                    break
                buf = data["data"]  # 每条是 [ts, o, h, l, c, vol, volCcy, volCcyQuote, confirm]

            # 本批数据按时间从新到旧排列, 最后一条是最旧的
            rows_this_batch = []
            for item in buf:
                ts = int(item[0])
                # 如果已经早于 start_ts，就跳过，并认为后面更旧，也可以结束循环
                if ts < start_ts:
                    continue
                # 如果某些条目时间超出 end_ts，也跳过
                if ts > end_ts:
                    continue
                # 解析数值字段
                dt = pd.to_datetime(ts, unit='ms', utc=True)
                o = float(item[1]); h = float(item[2]); l = float(item[3]); c = float(item[4]); vol = float(item[5])
                # 按需把每个 K 线封装为字典，后续转换为 DataFrame
                rows_this_batch.append({
                    "symbol": symbol,
                    "open_time": dt,
                    "open": o,
                    "high": h,
                    "low": l,
                    "close": c,
                    "volume": vol,
                    "interval": interval,
                    "confirm": item[8]
                })

            if not rows_this_batch:
                # 本批没有符合时间范围的数据，直接结束
                break

            # 累积本批符合条件的行
            all_rows.extend(rows_this_batch)

            # 检查是否到达 start_ts 之前：buf 最后一项是最旧
            oldest_ts = int(buf[-1][0])
            if oldest_ts < start_ts:
                # 已经翻到 start_time 范围之前，结束循环
                break

            # 否则，更新 after = oldest_ts，继续向过去翻页
            current_after = oldest_ts
            # 为了不触发速率限制，稍做休眠（根据需要可以调整或删除）

        # 如果累积到数据，则转换为 DataFrame；否则返回空 DataFrame
        if all_rows:
            df = pd.DataFrame(all_rows)
            # 去重、按时间排序
            df.drop_duplicates(subset=["open_time"], inplace=True)
            df.sort_values("open_time", inplace=True)
            df.reset_index(drop=True, inplace=True)
            return df
        else:
            return pd.DataFrame()

    async def get_index_klines(self, pair: str, interval: str, start_time, end_time=None, limit: int = 100):
        """
        获取OKX指数K线数据（自动分批）

        :param pair: 指数名称, 如 'BTC-USD'
        :param interval: K线间隔, 如 '1m', '1H', '1D'
        :param start_time: 开始时间(毫秒时间戳/datetime/date)
        :param end_time: 结束时间(毫秒时间戳/datetime/date)
        :param limit: 每次请求最大数量(OKX最大300)
        :return: DataFrame格式的指数K线
        """
        url = f"{self.base_url}/index-candles"
        all_klines = []
        ms_start = _to_milliseconds(start_time)
        ms_end = _to_milliseconds(end_time) if end_time else None

        params = {
            "instId": pair,
            "bar": interval,
            "limit": min(limit, 300),
            "after": ms_start
        }
        if ms_end:
            params["before"] = ms_end

        while True:
            async with self.session.get(url, params=params) as resp:
                data = await resp.json()
                if data['code'] != "0":
                    raise Exception(f"OKX API Error: {data['msg']} (Code {data['code']})")

                klines = data['data']
                if not klines:
                    break

                all_klines.extend(klines)

                if len(klines) < params["limit"]:
                    break

                last_ts = int(klines[-1][0])
                params["after"] = last_ts

        # 数据转换
        columns = ["open_time", "open", "high", "low", "close", "confirm"]
        df = pd.DataFrame(all_klines, columns=columns)

        df["open_time"] = pd.to_datetime(df["open_time"].astype(int), unit="ms")
        num_cols = ["open", "high", "low", "close"]
        df[num_cols] = df[num_cols].apply(pd.to_numeric, errors="coerce")

        return df.sort_values("open_time").reset_index(drop=True)

    async def close(self):
        """关闭会话"""
        await self.session.close()

    # 使用示例
    # async with OKXSwap() as okx:
    #     df = await okx.get_klines("BTC-USDT", "1H", datetime(2023,1,1))