"""
Coinglass API 数据解密与数据获取模块
优化：
- 只保留必要依赖，整理import顺序
- 增加类型注解和文档
- 统一异常处理和日志输出
- 精简冗余代码
"""
import asyncio
import base64
import json
import struct
import time
import zlib
import hmac
import hashlib
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
import pandas as pd # type: ignore
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding as crypto_padding
from cryptography.hazmat.backends import default_backend
import aiohttp

# ------------------ 工具函数 ------------------
class CustomParser:
    @staticmethod
    def parse(data: str) -> Dict[str, Union[List[int], int]]:
        """
        将字符串转换为数字数组，兼容原始加密逻辑。
        """
        length = len(data)
        n = [0] * ((length + 3) // 4)
        for r in range(length):
            n[r >> 2] |= (ord(data[r]) & 255) << (24 - (r % 4) * 8)
        return {"n": n, "e": length}

def convert_words_to_bytes(words: List[int]) -> bytes:
    """
    将整数数组转换为字节数组。
    """
    return b"".join(struct.pack(">I", word) for word in words)

def decrypt_and_clean(t: str, e: Dict[str, Any]) -> str:
    """
    解密、解压缩并清理输入字符串。
    """
    aes_key = convert_words_to_bytes(e['n'])
    cipher = Cipher(algorithms.AES(aes_key), modes.ECB(), backend=default_backend())
    decryptor = cipher.decryptor()
    encrypted_data = base64.b64decode(t)
    decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()
    unpadder = crypto_padding.PKCS7(128).unpadder()
    unpadded_data = unpadder.update(decrypted_data) + unpadder.finalize()
    decompressed_data = zlib.decompress(unpadded_data, wbits=16 + zlib.MAX_WBITS).decode('utf-8')
    return decompressed_data

def generate_totp(secret: str, for_time: int, interval: int = 30, digits: int = 6, digest=hashlib.sha1) -> str:
    """
    基于标准库的TOTP实现。
    """
    key = base64.b32decode(secret, casefold=True)
    counter = int(for_time // interval)
    msg = counter.to_bytes(8, 'big')
    h = hmac.new(key, msg, digest).digest()
    o = h[-1] & 0x0F
    code = (struct.unpack('>I', h[o:o+4])[0] & 0x7fffffff) % (10 ** digits)
    return str(code).zfill(digits)

def generate_encrypted_token() -> str:
    """
    生成加密token，用于API请求。
    """
    current_time = int(time.time())
    secret_key = "I65VU7K5ZQL7WB4E"
    otp = generate_totp(secret_key, current_time)
    combined_string = f"{current_time},{otp}"
    aes_key = "1f68efd73f8d4921acc0dead41dd39bc"
    aes_key_bytes = CustomParser.parse(aes_key)
    final_key = convert_words_to_bytes(aes_key_bytes['n'])
    cipher = Cipher(algorithms.AES(final_key), modes.ECB(), backend=default_backend())
    encryptor = cipher.encryptor()
    padder = crypto_padding.PKCS7(128).padder()
    padded_data = padder.update(combined_string.encode('utf-8')) + padder.finalize()
    encrypted_bytes = encryptor.update(padded_data) + encryptor.finalize()
    return base64.b64encode(encrypted_bytes).decode('utf-8')

def decrypt_coinglass(data: str, user_header: str, url: str) -> str:
    """
    解密 Coinglass API 的响应数据。
    """
    base_key = base64.b64encode(f"coinglass{url}coinglass".encode("utf-8")).decode("utf-8")[:16]
    processed_key = CustomParser.parse(base_key)
    decrypted_key = decrypt_and_clean(user_header, processed_key)
    session_key = decrypt_and_clean(data, CustomParser.parse(decrypted_key))
    return session_key

# ------------------ API类 ------------------
HEADERS = {
    'accept': 'application/json',
    'accept-language': 'en-US,en;q=0.9',
    'cache-ts': str(int(time.time() * 1000)),
    'dnt': '1',
    'encryption': 'true',
    'language': 'en',
    'origin': 'https://www.coinglass.com',
    'priority': 'u=1, i',
    'referer': 'https://www.coinglass.com/',
    'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
}

class CoinglassApi:
    def __init__(self) -> None:
        self.session = aiohttp.ClientSession()

    async def connect(self):
        pass

    async def dec_data(self, response: aiohttp.ClientResponse) -> Optional[Any]:
        try:
            encrypted_data = (await response.json())['data']
            requests_url = response.url.path
            encrypted_user_header = response.headers.get("user", "HEADERNOTFOUND")
            decrypted = decrypt_coinglass(encrypted_data, encrypted_user_header, requests_url)
            return json.loads(decrypted)
        except Exception as e:
            print(f"解密失败: {e}")
            return None

    async def fetch_base_klines(self, symbol: str, start_time: datetime, end_time: Optional[datetime] = None, ktype: str = '#coin#oi_kline', interval: str = 'm1') -> Any:
        start_ts = int(start_time.timestamp())
        end_ts = int(end_time.timestamp()) if end_time else int(time.time())
        url = 'https://fapi.coinglass.com/api/v2/kline'
        params = {
            'symbol': f'{symbol}{ktype}',
            'interval': interval,
            'endTime': end_ts,
            'startTime': start_ts,
            'minLimit': 'false',
        }
        async with self.session.get(url, params=params, headers=HEADERS) as response:
            if response.status == 200:
                return await self.dec_data(response)
            print(f"请求失败，状态码: {response.status}: {await response.text()}")
            return pd.DataFrame()

    async def fetch_price_klines(self, symbol: str, start_time: datetime, end_time: Optional[datetime] = None, interval: str = 'm5') -> pd.DataFrame:
        data = await self.fetch_base_klines(symbol, start_time, end_time, '#kline', interval)
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df[['open', 'high', 'low', 'close', 'volume']] = df[['open', 'high', 'low', 'close', 'volume']].astype(float)
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit="s", utc=True)
        df['symbol'] = symbol
        return df

    async def fetch_top_account_klines(self, symbol: str, start_time: datetime, end_time: Optional[datetime] = None, interval: str = 'm5') -> Optional[pd.DataFrame]:
        end_ts = int(end_time.timestamp()) if end_time else int(time.time())
        start_ts = int(start_time.timestamp())
        url = 'https://fapi.coinglass.com/api/v2/kline'
        params = {
            'symbol': f'{symbol}#top_account_kline',
            'interval': interval,
            'endTime': end_ts,
            'startTime': start_ts,
            'minLimit': 'false',
        }
        async with self.session.get(url, params=params, headers=HEADERS) as response:
            if response.status == 200:
                data = await self.dec_data(response)
                columns = ['timestamp', 'ratio', 'long_ratio', 'short_ratio']
                df = pd.DataFrame(data, columns=columns)
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit="s", utc=True)
                df[['ratio', 'long_ratio', 'short_ratio']] = df[['ratio', 'long_ratio', 'short_ratio']].astype(float)
                df['symbol'] = symbol
                return df
            print(f"请求失败，状态码: {response.status}: {await response.text()}")
            return None

    async def fetch_oi_klines(self, symbol: str, start_time: datetime, end_time: Optional[datetime] = None, interval: str = 'm5') -> pd.DataFrame:
        data = await self.fetch_base_klines(symbol, start_time, end_time, '#coin#oi_kline', interval)
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close'])
        df[['open', 'high', 'low', 'close']] = df[['open', 'high', 'low', 'close']].astype(float)
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit="s", utc=True)
        df['symbol'] = symbol
        return df

    async def fetch_liq_klines(self, symbol: str, start_time: datetime, end_time: Optional[datetime] = None, interval: str = 'm5') -> pd.DataFrame:
        data = await self.fetch_base_klines(symbol, start_time, end_time, '#aggregated_liq_kline', interval)
        df = pd.DataFrame(data, columns=['timestamp', 'short_amount', 'long_amount'])
        df[['short_amount', 'long_amount']] = df[['short_amount', 'long_amount']].astype(float)
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit="s", utc=True)
        df['symbol'] = symbol
        return df

    async def fetch_hyperliquid_top_positions(self) -> Optional[Any]:
        url = 'https://capi.coinglass.com/api/hyperliquid/topPosition'
        async with self.session.get(url, headers=HEADERS) as response:
            if response.status == 200:
                return await self.dec_data(response)
            print(f"请求失败，状态码: {response.status}: {await response.text()}")
            return None

    async def fetch_tickers(self) -> Optional[Any]:
        url = 'https://fapi.coinglass.com/api/select/coins/tickers'
        params = {'exName': 'Binance'}
        async with self.session.get(url, params=params, headers=HEADERS) as response:
            if response.status == 200:
                return await self.dec_data(response)
            print(f"请求失败，状态码: {response.status}: {await response.text()}")
            return None

    async def fetch_symbols(self, only_usdt: bool = True) -> List[str]:
        tickers = await self.fetch_tickers()
        if tickers:
            symbols = [ticker['instrument']['instrumentId'] for ticker in tickers]
            if only_usdt:
                symbols = [symbol for symbol in symbols if symbol.endswith('USDT')]
            return symbols
        return []

    async def stop(self):
        await self.session.close()

# ------------------ 主程序 ------------------
async def main():
    api = CoinglassApi()
    df = await api.fetch_price_klines('Binance_BTCUSDT', datetime.now() - timedelta(days=1))
    print(df)
    await api.stop()

if __name__ == '__main__':
    asyncio.run(main())