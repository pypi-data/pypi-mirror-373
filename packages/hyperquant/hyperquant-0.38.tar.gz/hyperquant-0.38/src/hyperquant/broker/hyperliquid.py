# hyperliquid_trader_optimized.py
"""Async wrapper around Hyperliquid REST + WebSocket endpoints.

Key design goals
----------------
* **Single point of truth** – all endpoint paths & constants live at module scope.
* **Safety** – every public coroutine is fully‑typed and guarded with rich
  error messages; internal state is protected by an `asyncio.Lock` where
  necessary.
* **Performance** – expensive metadata is fetched once and cached; price/size
  formatting uses the `decimal` module only when needed.
* **Ergonomics** – high‑level order helpers (`buy`, `sell`) are provided on top
  of the generic `place_order` routine; context‑manager semantics make sure
  network resources are cleaned up.
"""
from __future__ import annotations

import asyncio
import decimal
import itertools
import logging
from dataclasses import dataclass
import time
from typing import Any, Dict, Optional

import pybotters
from yarl import URL

from .models.hyperliquid import MyHyperStore

def to_cloid(s: str) -> str:
    """
    可逆地将字符串转为 Hyperliquid cloid 格式（要求字符串最多16字节，超出报错）。
    :param s: 原始字符串
    :return: 形如0x...的cloid字符串
    """
    b = s.encode('utf-8')
    if len(b) > 16:
        raise ValueError("String too long for reversible cloid (max 16 bytes)")
    # 补齐到16字节
    b = b.ljust(16, b'\0')
    return "0x" + b.hex()

def cloid_to_str(cloid: str) -> str:
    """
    从cloid还原回原始字符串
    :param cloid: 形如0x...的cloid字符串
    :return: 原始字符串
    """
    try:
        if not (cloid.startswith("0x") and len(cloid) == 34):
            raise ValueError("Invalid cloid format for reversal")
        b = bytes.fromhex(cloid[2:])
        return b.rstrip(b'\0').decode('utf-8')
    except Exception as e:
        return ''


__all__ = [
    "HyperliquidTrader",
]

_API_BASE_MAIN = "https://api.hyperliquid.xyz"
_API_BASE_TEST = "https://api.hyperliquid-testnet.xyz"
_WSS_URL_MAIN = "wss://api.hyperliquid.xyz/ws"
_WSS_URL_TEST = "wss://api.hyperliquid-testnet.xyz/ws"
_INFO = "/info"
_EXCHANGE = "/exchange"

logger = logging.getLogger(__name__)


# ╭─────────────────────────────────────────────────────────────────────────╮
# │                                Helpers                                 │
# ╰─────────────────────────────────────────────────────────────────────────╯
@dataclass(frozen=True, slots=True)
class AssetMeta:
    """Metadata for a tradable asset."""

    asset_id: int
    name: str
    sz_decimals: int
    tick_size: float = None

@dataclass(frozen=True, slots=True)
class SpotAssetMeta:
    """Metadata for a tradable asset."""

    asset_id: int # eg. 10000
    name: str # eg. "#173"
    sz_decimals: int # eg. 2
    index: int # eg. 0
    token_name: str # eg. "FEUSD"
    mark_price: float = None

@dataclass
class OrderData():
    o_id: str = ''
    c_id: str = ''
    name: str = ''
    status: str = 'resting'
    price: float = None
    sz: float = None


_DECIMAL_CTX_5 = decimal.Context(prec=5)

def normalize_number(n):
    # 能去掉小数点后多余的零
    return format(decimal.Decimal(str(n)).normalize(), "f")

def _fmt_price(price: float, sz_decimals: int, *, max_decimals: int = 6) -> float:
    """
    格式化价格：
      - 大于100000直接取整数
      - 其它情况保留5个有效数字，然后再按max_decimals-sz_decimals截断小数位
    """
    if price > 100_000:
        return str(round(price))
    # 先保留5个有效数字，再截断小数位
    price_5sf = float(f"{price:.5g}")
    return normalize_number(round(price_5sf, max_decimals - sz_decimals))

def _fmt_size(sz: float, sz_decimals: int) -> float:
    """
    格式化数量：直接按 sz_decimals 小数位截断
    """
    return normalize_number(round(sz, sz_decimals))


# ╭─────────────────────────────────────────────────────────────────────────╮
# │                           Public main class                            │
# ╰─────────────────────────────────────────────────────────────────────────╯
class HyperliquidTrader:
    """High‑level async client for Hyperliquid."""

    def __init__(
        self,
        apis: str | dict | None = None,
        *,
        client: Optional[pybotters.Client] = None,
        user_address: Optional[str] = None,
        msg_callback: Optional[callable[[dict, pybotters.ws.WebSocketAppProtocol], None]] = None,
        testnet: bool = False,
    ) -> None:
        self._external_client = client is not None
        self._client: pybotters.Client | None = client
        self._apis = apis
        self._user = user_address
        self._msg_cb_user = msg_callback

        self._testnet = testnet
        self._api_base = _API_BASE_TEST if testnet else _API_BASE_MAIN
        self._wss_url = _WSS_URL_TEST if testnet else _WSS_URL_MAIN

        self._assets: dict[str, AssetMeta] = {}
        self._spot_assets: dict[str, SpotAssetMeta] = {}

        self._assets_with_name: dict[str, AssetMeta] = {}
        self._spot_assets_with_name: dict[str, SpotAssetMeta] = {}

        self._next_id = itertools.count().__next__  # fast thread‑safe counter
        self._waiters: dict[int, asyncio.Future[dict[str, Any]]] = {}
        self._waiter_lock = asyncio.Lock()

        self._ws_app: Optional[pybotters.ws.WebSocketConnection] = None
        self.store: MyHyperStore = MyHyperStore()
        


    # ──────────────────────────────────────────────────────────────────────
    # Lifecyle helpers
    # ──────────────────────────────────────────────────────────────────────
    async def __aenter__(self) -> "HyperliquidTrader":
        if self._client is None:
            self._client = await pybotters.Client(apis=self._apis, base_url=self._api_base).__aenter__()

        await self._fetch_meta()
        await self._fech_spot_meta()

        self._ws_app:pybotters.WebSocketApp = await self._client.ws_connect(
            self._wss_url,
            send_json=[],
            hdlr_json=self._dispatch_msg,
        )

        if self._user:
            await self.store.initialize(
                ("orders", self._client.post(_INFO, data={"type": "openOrders", "user": self._user})),
                ("positions", self._client.post(_INFO, data={"type": "clearinghouseState", "user": self._user})),
            )
            self._client.ws_connect(
                self._wss_url,
                send_json=[
                {
                    "method": "subscribe",
                    "subscription": {
                        "type": "orderUpdates",
                        "user": self._user,
                    },
                }, 
                {
                    "method": "subscribe",
                    "subscription": {
                        "type": "userFills",
                        "user": self._user,
                    },
                }, 
                {
                    "method": "subscribe",
                    "subscription": {
                        "type": "webData2",
                        "user": self._user,
                    },
                }],
                hdlr_json=self.store.onmessage,
            )

        return self

    async def __aexit__(self, exc_type, exc, tb):  # noqa: D401
        if not self._external_client and self._client is not None:
            await self._client.__aexit__(exc_type, exc, tb)
    
    async def sync_orders(self):
        await self.store.orders._clear()
        await self.store.initialize(
            ("orders", self._client.post(_INFO, data={"type": "openOrders", "user": self._user})),
        )

    # ──────────────────────────────────────────────────────────────────────
    # Internal – metadata & formatting helpers
    # ──────────────────────────────────────────────────────────────────────
    async def _fetch_meta(self) -> None:
        assert self._client is not None  # mypy
        resp = await self._client.fetch("POST", _INFO, data={"type": "meta"})
        if not resp.data:
            raise RuntimeError(f"Failed to fetch meta: {resp.error}")

        self._assets = {
            d["name"]: AssetMeta(asset_id=i, name=d["name"], sz_decimals=d["szDecimals"], tick_size=10**(d["szDecimals"] - 6))
            for i, d in enumerate(resp.data["universe"])
        }

        logger.debug("Loaded %d assets", len(self._assets))

    async def _fech_spot_meta(self) -> None:
        assert self._client is not None  # mypy
        resp = await self._client.fetch("POST", _INFO, data={"type": "spotMeta"})
        if not resp.data:
            raise RuntimeError(f"Failed to fetch meta: {resp.error}")

        metadata = resp.data

        tokens = metadata['tokens']

        for u in metadata['universe']:
            coin_name = u['name']
            index = u['index']
            tk_id = u['tokens'][0]
            token_name = tokens[tk_id]['name']
            szDecimals = tokens[tk_id]['szDecimals']

            meta =  SpotAssetMeta(
                asset_id= 10000 + index,
                name=coin_name,
                sz_decimals=szDecimals,
                index=index,
                token_name=token_name,
                mark_price=0.0,
            )
            self._spot_assets[token_name] = meta
            self._spot_assets_with_name[coin_name] = meta

        

    def _asset(self, symbol: str, is_spot: bool = False) -> AssetMeta:
        try:
            if is_spot:
                return self._spot_assets[symbol]
            else:
                return self._assets[symbol]
        except KeyError as exc:
            raise ValueError(f"Unknown asset '{symbol}'. Have you called __aenter__()?") from exc
        
    def fmt_price(self, price: float, symbol: str, is_spot: bool = False) -> float:
        asset = self._asset(symbol, is_spot=is_spot)
        return float(_fmt_price(price, asset.sz_decimals))
    
    def fmt_size(self, size: float, symbol: str, is_spot: bool = False) -> float:
        asset = self._asset(symbol, is_spot=is_spot)
        return float(_fmt_size(size, asset.sz_decimals))
        

    def sub_l2_book(self, symbol: str, is_spot: bool = False) -> None:

        asset = self._asset(symbol, is_spot=is_spot)
        
        self._client.ws_connect(
            self._wss_url,
            send_json={
                "method": "subscribe",
                "subscription": {
                    "type": "l2Book",
                    "coin": asset.name,
                },
            },
            hdlr_json=self.store.onmessage
        )
  

    # ──────────────────────────────────────────────────────────────────────
    # Internal – WebSocket message routing
    # ──────────────────────────────────────────────────────────────────────
    def _dispatch_msg(self, msg: dict[str, Any], wsapp):  # noqa: ANN001
        mid = msg.get("data", {}).get("id")
        if mid is not None:
            fut = self._waiters.pop(mid, None)
            if fut and not fut.done():
                fut.set_result(msg)
                return
        # fallback: hand over to user callback / buffer
        if self._msg_cb_user is not None:
            self._msg_cb_user(msg, wsapp)
        else:
            logger.debug("Unhandled WS message: %s", msg)

    async def _wait_for_id(self, rid: int) -> dict[str, Any]:
        async with self._waiter_lock:
            fut = self._waiters[rid] = asyncio.get_event_loop().create_future()
        return await fut

    # ──────────────────────────────────────────────────────────────────────
    # REST helpers
    # ──────────────────────────────────────────────────────────────────────
    async def _post(self, path: str, data: dict[str, Any]):
        assert self._client is not None
        info = await self._client.fetch("POST", path, data=data)
        info.response.raise_for_status()
        return info.data

    # ──────────────────────────────────────────────────────────────────────
    # Public API – account
    # ──────────────────────────────────────────────────────────────────────
    async def balances(self, user: Optional[str] = None):  # todo support spot
        try:
            user = user or self._user
            if user is None:
                raise ValueError("User address required – pass it now or in constructor")
            data = await self._post(_INFO, {"type": "clearinghouseState", "user": user})
            match data:
                case pybotters.NotJSONContent():
                    print('可能参数有误')
                    return None
            return data    
        except Exception as e:
            print(f"Error fetching balances: {e}")
            return None

    async def open_orders(self, user: Optional[str] = None):
        user = user or self._user
        if user is None:
            raise ValueError("User address required – pass it now or in constructor")
        return await self._post(_INFO, {"type": "openOrders", "user": user})

    async def cancel_order(
        self,
        asset: str,
        order_id: str,
        *,
        use_ws: bool = False,
        is_spot: bool = False,
    ) -> dict[str, Any]:

        meta = self._asset(asset, is_spot=is_spot)
        
        payload = {
            "action": {
                "type": "cancel",
                "cancels": [{"a": meta.asset_id, "o": order_id}],
            }
        }



        if not use_ws:
            return await self._post(_EXCHANGE, payload)

        signed = await self._ws_sign(payload)
        assert self._ws_app is not None
        await self._ws_app.current_ws.send_json(signed)
        return order_id
    
    async def cancel_all_orders(
        self,
        asset: Optional[str] = None,
        *,
        use_ws: bool = False,
        is_spot: bool = False,
    ) -> dict[str, Any]:
        # [{'coin': '@153', 'side': 'A', 'limitPx': '0.9904', 'sz': '202.33', 'oid': 93287495240, 'timestamp': 1747118448026, 'origSz': '202.33', 'cloid': '0x441f6c3b8dde4ccfb34a24ec23419f2d'}, {'coin': '@153', 'side': 'B', 'limitPx': '0.9864', 'sz': '202.76', 'oid': 93278072490, 'timestamp': 1747115006552, 'origSz': '202.76', 'cloid': '0x90fac8c56d224a20b4fd0ab6cf4eae5e'}]
        orders = await self.open_orders()
        
        if asset:
            meta = self._asset(asset, is_spot=is_spot)
            orders = [o for o in orders if o['coin'] == meta.name]
 
        if is_spot:
            for o in orders:
                o['asset_id'] = self._spot_assets_with_name[o['coin']].asset_id
        else:
            for o in orders:
                o['asset_id'] = self._asset(o['coin']).asset_id

        # 构建payload
        payload = {
            "action": {
                "type": "cancel",
                "cancels": [
                    {"a": o['asset_id'], "o": o['oid']}
                    for o in orders
                ],
            }
        }
        print(payload)

        if not use_ws:
            return await self._post(_EXCHANGE, payload)
        signed = await self._ws_sign(payload)
        assert self._ws_app is not None
        await self._ws_app.current_ws.send_json(signed)
        return orders

    
    async def get_mid(self, asset: str, is_spot: bool = False) -> float:
        """Get the mid price of an asset."""
        meta = self._asset(asset, is_spot=is_spot)
        book = await self._post(_INFO, {"type": "l2Book", "coin": meta.name})
        bid = float(book["levels"][0][0]["px"])
        ask = float(book["levels"][1][0]["px"])
        return float(_fmt_price((bid + ask) / 2, meta.sz_decimals))
    
    async def get_books(self, asset: str, is_spot: bool = False) -> list[float]:
        """Get the ask prices of an asset."""
        meta = self._asset(asset, is_spot=is_spot)
        book = await self._post(_INFO, {"type": "l2Book", "coin": meta.name})
        levels = book["levels"]
        bids = levels[0]
        asks = levels[1]
        return {
            "bids": bids,
            "asks": asks,
        }

    # ──────────────────────────────────────────────────────────────────────
    # Public API – trading
    # ──────────────────────────────────────────────────────────────────────
    async def place_order(
        self,
        asset: str,
        *,
        side: str = "buy",  # "buy" | "sell"
        order_type: str = "market",  # "market" | "limit"
        size: float,
        slippage: float = 0.02,
        price: Optional[float] = None,  # required for limit orders
        use_ws: bool = False,
        is_spot: bool = False,
        reduce_only: bool = False,  # whether to place a reduce‑only order
        cloid: Optional[str] = None, 
    ) -> OrderData:
        """`place_order` 下订单

        返回值:
         'OrderData'
        """
        meta = self._asset(asset, is_spot=is_spot)
        is_buy = side.lower() == "buy"

        if order_type == "limit":
            if price is None:
                raise ValueError("price must be supplied for limit orders")
            price_str = _fmt_price(price, meta.sz_decimals)
            tif = "Gtc"
        else:
            # emulate market by crossing the spread via mid ± slippage
            if price is None:
                mid = await self.get_mid(asset, is_spot=is_spot)
            else:
                mid = price  # allow user‑supplied mid for testing
            crossed = mid * (1 + slippage) if is_buy else mid * (1 - slippage)
            price_str = _fmt_price(crossed, meta.sz_decimals)
            tif = "Ioc"

        size_str = _fmt_size(size, meta.sz_decimals)
        # print(f'下单 @ size_str: {size_str}, price_str: {price_str}, asset: {asset}, is_spot: {is_spot}')
        order_payload = {
            "action": {
                "type": "order",
                "orders": [
                    {
                        "a": meta.asset_id,
                        "b": is_buy,
                        "p": price_str,
                        "s": size_str,
                        "r": reduce_only,
                        "t": {"limit": {"tif": tif}},
                    }
                ],
                "grouping": "na",
            }
        }
        if cloid is not None:
            if not cloid.startswith("0x"):
                cloid = to_cloid(cloid)
            
            order_payload["action"]["orders"][0]["c"] = cloid

        # print(f"Placing order: {order_payload}")
        # print(order_payload)

        if not use_ws:
            ret = await self._post(_EXCHANGE, order_payload)
            print(ret)
            if 'error' in str(ret) or 'err' in str(ret):
                raise RuntimeError(f"Failed to place order: {ret}")
            elif 'filled' in str(ret):
                return OrderData(
                    o_id=ret['response']['data']['statuses'][0]['filled']['oid'],
                    c_id=cloid,
                    name=asset,
                    status='filled',
                    price=float(ret['response']['data']['statuses'][0]['filled']['avgPx']),
                    sz=float(ret['response']['data']['statuses'][0]['filled']['totalSz']),
                )
            elif 'resting' in str(ret):
                return OrderData(
                    o_id=ret['response']['data']['statuses'][0]['resting']['oid'],
                    c_id=cloid,
                    price=float(price_str),
                    name=asset,
                    status='resting',
                )

        # else – signed WS flow
        signed = await self._ws_sign(order_payload)
        assert self._ws_app is not None
        await self._ws_app.current_ws.send_json(signed)
        return OrderData(o_id=cloid, name=asset, price=float(price_str))

    # Convenience wrappers -------------------------------------------------
    async def buy(self, asset: str, **kw):
        return await self.place_order(asset, side="buy", **kw)

    async def sell(self, asset: str, **kw):
        return await self.place_order(asset, side="sell", **kw)

    # ──────────────────────────────────────────────────────────────────────
    # Internal – signing helper
    # ──────────────────────────────────────────────────────────────────────
    async def _ws_sign(self, payload):  # noqa: ANN001 – hyperliquid internal format
        # mimic pybotters signing util for WS‑POST messages
        url = URL(f"{self._api_base}/abc")
        pybotters.Auth.hyperliquid((None, url), {"data": payload, "session": self._client._session})  # type: ignore[attr-defined]
        rid = self._next_id()
        return {
            "method": "post",
            "id": rid,
            "request": {"type": "action", "payload": payload},
        }
