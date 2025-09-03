from __future__ import annotations

import asyncio
import logging
import time
from typing import TYPE_CHECKING, Any, Awaitable

import aiohttp
from pybotters.store import DataStore, DataStoreCollection

if TYPE_CHECKING:
    from pybotters.typedefs import Item
    from pybotters.ws import ClientWebSocketResponse


logger = logging.getLogger(__name__)


class Book(DataStore):
    """深度数据存储类，用于处理订单簿深度信息

    Channel: push.depth.step

    用于存储和管理订单簿深度数据，包含买卖盘的价格和数量信息
    Keys: ["symbol", "side", "px"]
    - symbol: 交易对符号
    - side: 买卖方向 (A: ask卖出, B: bid买入)
    - px: 价格


    """

    _KEYS = ["symbol", "side",  "i"]

    def _init(self) -> None:
        # super().__init__()
        self._time: int | None = None

    def _on_message(self, msg: dict[str, Any]) -> None:

        symbol = msg.get("symbol")
        data = msg.get("data", {})
        asks = data.get("asks", [])
        bids = data.get("bids", [])
        # 提速 默认 5当前
        asks = asks[:5]
        bids = bids[:5]

        timestamp = data.get("ct")  # 使用服务器时间

        data_to_insert: list[Item] = []

        # 先删除旧的订单簿数据
        self._find_and_delete({"symbol": symbol})

        # 处理买卖盘数据
        for side_id, levels in (("B", bids), ("A", asks)):
            for i, level in enumerate(levels):
                # level格式: [price, size, count]
                if len(level) >= 3:
                    price, size, count = level[0:3]
                    data_to_insert.append(
                        {
                            "symbol": symbol,
                            "side": side_id,
                            "px": str(price),
                            "sz": str(size),
                            "count": count,
                            "i": i
                        }
                    )

        # 插入新的订单簿数据
        self._insert(data_to_insert)
        self._time = timestamp

    @property
    def time(self) -> int | None:
        """返回最后更新时间"""
        return self._time

    @property
    def sorted(self) -> dict[str, list[Item]]:
        """获取排序后的订单簿数据

        Returns:
            返回按价格排序的买卖盘数据，卖盘升序，买盘降序

        .. code-block:: python

            {
                "asks": [
                    {"symbol": "BTC_USDT", "side": "A", "px": "110152.5", "sz": "53539", "count": 1},
                    {"symbol": "BTC_USDT", "side": "A", "px": "110152.6", "sz": "95513", "count": 2}
                ],
                "bids": [
                    {"symbol": "BTC_USDT", "side": "B", "px": "110152.4", "sz": "76311", "count": 1},
                    {"symbol": "BTC_USDT", "side": "B", "px": "110152.3", "sz": "104688", "count": 2}
                ]
            }
        """
        return self._sorted(
            item_key="side",
            item_asc_key="A",  # asks 升序
            item_desc_key="B",  # bids 降序
            sort_key="px",
        )


class Ticker(DataStore):
    _KEYS = ["symbol"]

    def _on_message(self, data: dict[str, Any]):
        self._onresponse(data)

    def _onresponse(self, data: dict[str, Any]):
        tickers = data.get("data", [])
        if tickers:
            data_to_insert: list[Item] = []
            for ticker in tickers:
                ticker: dict[str, Any] = ticker
                for ticker in tickers:
                    data_to_insert.append(
                        {
                            "amount24": ticker.get("amount24"),
                            "fair_price": ticker.get("fairPrice"),
                            "high24_price": ticker.get("high24Price"),
                            "index_price": ticker.get("indexPrice"),
                            "last_price": ticker.get("lastPrice"),
                            "lower24_price": ticker.get("lower24Price"),
                            "max_bid_price": ticker.get("maxBidPrice"),
                            "min_ask_price": ticker.get("minAskPrice"),
                            "rise_fall_rate": ticker.get("riseFallRate"),
                            "symbol": ticker.get("symbol"),
                            "timestamp": ticker.get("timestamp"),
                            "volume24": ticker.get("volume24"),
                        }
                    )
            # self._clear()
            self._insert(data_to_insert)


class Orders(DataStore):
    _KEYS = ["order_id"]

    def _fmt(self, order:dict):
        return {
            "order_id": order.get("orderId"),
            "symbol": order.get("symbol"),
            "px": order.get("price"),
            "vol": order.get("vol"),
            "lev": order.get("leverage"),
            "side": "buy" if order.get("side") == 1 else "sell",
            "deal_vol": order.get("dealVol"),
            "deal_avg_px": order.get("dealAvgPrice"),
            "create_ts": order.get("createTime"),
            "update_ts": order.get("updateTime"),
            "state": "open"
        }

    # {'success': True, 'code': 0, 'data': [{'orderId': '219108574599630976', 'symbol': 'SOL_USDT', 'positionId': 0, 'price': 190, 'priceStr': '190', 'vol': 1, 'leverage': 20, 'side': 1, 'category': 1, 'orderType': 1, 'dealAvgPrice': 0, 'dealAvgPriceStr': '0', 'dealVol': 0, 'orderMargin': 0.09652, 'takerFee': 0, 'makerFee': 0, 'profit': 0, 'feeCurrency': 'USDT', 'openType': 1, 'state': 2, 'externalOid': '_m_2228b23a75204e1982b301e44d439cbb', 'errorCode': 0, 'usedMargin': 0, 'createTime': 1756277955008, 'updateTime': 1756277955037, 'positionMode': 1, 'version': 1, 'showCancelReason': 0, 'showProfitRateShare': 0, 'voucher': False}]}
    def _onresponse(self, data: dict[str, Any]):
        orders = data.get("data", [])
        if orders:
            data_to_insert: list[Item] = []
            for order in orders:
                order: dict[str, Any] = order
                data_to_insert.append(self._fmt(order))

            self._clear()
            self._update(data_to_insert)
        
    def _on_message(self, msg: dict[str, Any]) -> None:
        data:dict = msg.get("data", {})
        if msg.get('channel') == 'push.personal.order':
            state = data.get("state")
            if state == 2:
                order = self._fmt(data)
                order["state"] = "open"
                self._insert([order])
            elif state == 3:
                order = self._fmt(data)
                order["state"] = "filled"
                self._update([order])
                self._find_and_delete({
                    "order_id": order.get("order_id")
                })
            elif state == 4:
                order = self._fmt(data)
                order["state"] = "canceled"
                self._update([order])
                self._find_and_delete({
                    "order_id": order.get("order_id")
                })

class Detail(DataStore):
    _KEYS = ["symbol"]

    def _on_message(self, data: dict[str, Any]):
        self._onresponse(data)

    def _onresponse(self, data: dict[str, Any]):
        details: dict = data.get("data", {})
        data_to_insert: list[Item] = []
        if details:
            for detail in details:
                data_to_insert.append(
                    {
                        "symbol": detail.get("symbol"),
                        "ft": detail.get("ft"),
                        "max_lev": detail.get("maxL"),
                        "tick_size": detail.get("pu"),
                        "vol_unit": detail.get("vu"),
                        "io": detail.get("io"),
                        "contract_sz": detail.get("cs"),
                        "minv": detail.get("minV"),
                        "maxv": detail.get("maxV")
                    }
                )
        self._update(data_to_insert)

class Position(DataStore):
    _KEYS = ["position_id"]
    # {"success":true,"code":0,"data":[{"positionId":5355366,"symbol":"SOL_USDT","positionType":1,"openType":1,"state":1,"holdVol":1,"frozenVol":0,"closeVol":0,"holdAvgPrice":203.44,"holdAvgPriceFullyScale":"203.44","openAvgPrice":203.44,"openAvgPriceFullyScale":"203.44","closeAvgPrice":0,"liquidatePrice":194.07,"oim":0.10253376,"im":0.10253376,"holdFee":0,"realised":-0.0008,"leverage":20,"marginRatio":0.0998,"createTime":1756275984696,"updateTime":1756275984696,"autoAddIm":false,"version":1,"profitRatio":0,"newOpenAvgPrice":203.44,"newCloseAvgPrice":0,"closeProfitLoss":0,"fee":0.00081376}]}
    
    def _fmt(self, position:dict):
        return {
                        "position_id": position.get("positionId"),
                        "symbol": position.get("symbol"),
                        "side": "short" if position.get("positionType") == 2 else "long",
                        "open_type": position.get("openType"),
                        "state": position.get("state"),
                        "hold_vol": position.get("holdVol"),
                        "frozen_vol": position.get("frozenVol"),
                        "close_vol": position.get("closeVol"),
                        "hold_avg_price": position.get("holdAvgPriceFullyScale"),
                        "open_avg_price": position.get("openAvgPriceFullyScale"),
                        "close_avg_price": str(position.get("closeAvgPrice")),
                        "liquidate_price": str(position.get("liquidatePrice")),
                        "oim": position.get("oim"),
                        "im": position.get("im"),
                        "hold_fee": position.get("holdFee"),
                        "realised": position.get("realised"),
                        "leverage": position.get("leverage"),
                        "margin_ratio": position.get("marginRatio"),
                        "create_ts": position.get("createTime"),
                        "update_ts": position.get("updateTime"),
            }
    
    def _onresponse(self, data: dict[str, Any]):
        positions = data.get("data", [])
        if positions:
            data_to_insert: list[Item] = []
            for position in positions:
                position: dict[str, Any] = position

                data_to_insert.append(
                    self._fmt(position)
                )

            self._clear()
            self._insert(data_to_insert)
        else:
            self._clear()

    def _on_message(self, msg: dict[str, Any]) -> None:
        data:dict = msg.get("data", {})
        state = data.get("state")
        position_id = data.get("positionId")
        if state == 3:
            self._find_and_delete({"position_id": position_id})
            return
        
        self._update([self._fmt(data)])

class Balance(DataStore):
    _KEYS = ["currency"]

    def _fmt(self, balance: dict) -> dict:
        return {
            "available_balance": balance.get("availableBalance"),
            "bonus": balance.get("bonus"),
            "currency": balance.get("currency"),
            "frozen_balance": balance.get("frozenBalance"),
            "last_bonus": balance.get("lastBonus"),
            "position_margin": balance.get("positionMargin"),
            "wallet_balance": balance.get("walletBalance"),
        }

    def _onresponse(self, data: dict[str, Any]):
        balances = data.get("data", [])
        if balances:
            data_to_insert: list[Item] = []
            for balance in balances:
                balance: dict[str, Any] = balance
                data_to_insert.append(self._fmt(balance))
            self._clear()
            self._insert(data_to_insert)
    
    def _on_message(self, msg: dict[str, Any]) -> None:
        data: dict = msg.get("data", {})
        self._update([self._fmt(data)])



class OurbitSwapDataStore(DataStoreCollection):
    """
    Ourbit DataStoreCollection

    REST API:
      - 地址: https://futures.ourbit.com
      - 合约详情
        GET /api/v1/contract/detailV2?client=web
      - ticker
        GET /api/v1/contract/ticker
      - open_orders
        GET /api/v1/private/order/list/open_orders?page_size=200
      - open_positions
        GET /api/v1/private/position/open_positions

    WebSocket API:
      - 地址: wss://futures.ourbit.com/edge or /ws
      - 支持频道:
        * 深度数据（Book）: push.depth.step
        * 行情数据（Ticker）: push.tickers

    示例订阅 JSON:

    .. code:: json

        {
            "method": "sub.depth.step",
            "param": {
                "symbol": "BTC_USDT",
                "step": "0.1"
            }
        }

    .. code:: json

        {
            "method": "sub.tickers",
            "param": {
                "timezone": "UTC+8"
            }
        }

    TODO:
      - 添加 trades、ticker、candle 等其他数据流
    """

    def _init(self) -> None:
        self._create("book", datastore_class=Book)
        self._create("detail", datastore_class=Detail)
        self._create("ticker", datastore_class=Ticker)
        self._create("orders", datastore_class=Orders)
        self._create("position", datastore_class=Position)
        self._create("balance", datastore_class=Balance)
        # TODO: 添加其他数据流，如 trades, ticker, candle 等

    def onmessage(self, msg: Item, ws: ClientWebSocketResponse | None = None) -> None:
        channel = msg.get("channel")

        if channel == "push.depth.step":
            self.book._on_message(msg)
        if channel == "push.tickers":
            self.ticker._on_message(msg)
        if channel == "push.personal.position":
            self.position._on_message(msg)
        if channel == "push.personal.order":
            self.orders._on_message(msg)
        if channel == "push.personal.asset":
            self.balance._on_message(msg)
        else:
            logger.debug(f"未知的channel: {channel}")

    async def initialize(self, *aws: Awaitable[aiohttp.ClientResponse]) -> None:
        """Initialize DataStore from HTTP response data."""
        for f in asyncio.as_completed(aws):
            res = await f
            data = await res.json()
            if res.url.path == "/api/v1/contract/detailV2":
                self.detail._onresponse(data)
            if res.url.path == "/api/v1/contract/ticker":
                self.ticker._onresponse(data)
            if res.url.path == "/api/v1/private/order/list/open_orders":
                self.orders._onresponse(data)
            if res.url.path == "/api/v1/private/position/open_positions":
                self.position._onresponse(data)
            if res.url.path == "/api/v1/private/account/assets":
                self.balance._onresponse(data)

    @property
    def detail(self) -> Detail:
        """合约详情
        Data structure:
        .. code:: python
        [
            {
                "symbol": "BTC_USDT",   # 交易对
                "ft": 100,            # 合约面值
                "max_lev": 100,       # 最大杠杆
                "tick_size": 0.1,     # 最小变动价位
                "vol_unit": 1,        # 合约单位
                "io": ["binance", "mexc"],  # 交易所列表
                "contract_sz": 1,
                "minv": 1,
                "maxv": 10000

            }
        ]
        """
        return self._get("detail", Detail)

    @property
    def book(self) -> Book:
        """订单簿深度数据流

        Data type: Mutable

        Keys: ("symbol", "side", "px")

        Data structure:

        .. code:: python

            [
                {
                    "symbol": "BTC_USDT",    # 交易对
                    "side": "A",             # 卖出方向
                    "px": "110152.5",        # 价格
                    "sz": "53539",           # 数量
                    "count": 1               # 订单数量
                    "i" 0                  # 价格档位索引
                },
                {
                    "symbol": "BTC_USDT",    # 交易对
                    "side": "B",             # 买入方向
                    "px": "110152.4",        # 价格
                    "sz": "76311",           # 数量
                    "count": 1               # 订单数量
                    "i" 0                  # 价格档位索引
                }
            ]
        """
        return self._get("book", Book)

    @property
    def ticker(self) -> Ticker:
        """市场行情数据流

        Data type: Mutable

        Keys: ("symbol",)

        Data structure:

        .. code:: python

            [
                {
                    "symbol": "BTC_USDT",        # 交易对
                    "last_price": "110152.5",    # 最新价格
                    "index_price": "110000.0",   # 指数价格
                    "fair_price": "110100.0",    # 公允价格
                    "high24_price": "115000.0",  # 24小时最高价
                    "lower24_price": "105000.0", # 24小时最低价
                    "volume24": "1500",          # 24小时交易量
                    "amount24": "165000000",     # 24小时交易额
                    "rise_fall_rate": "0.05",    # 涨跌幅
                    "max_bid_price": "110150.0", # 买一价
                    "min_ask_price": "110155.0", # 卖一价
                    "timestamp": 1625247600000   # 时间戳
                }
            ]
        """
        return self._get("ticker", Ticker)

    @property
    def orders(self) -> Orders:
        """
        订单数据
        Data structure:

        .. code:: json

            [
                {
                    "id": "123456",
                    "symbol": "BTC_USDT",
                    "side": "buy",
                    "price": "110152.5",
                    "size": "0.1",
                    "state": "open", // ("open", "closed", "canceled")
                    "create_ts": 1625247600000,
                    "update_ts": 1625247600000
                }
            ]
        """
        return self._get("orders", Orders)

    @property
    def position(self) -> Position:
        """
        持仓数据
        Data structure:

        .. code:: json

            [
                {
                    "position_id": "123456",
                    "symbol": "BTC_USDT",
                    "side": "long",
                    "open_type": "limit",
                    "state": "open",
                    "hold_vol": "0.1",
                    "frozen_vol": "0.0",
                    "close_vol": "0.0",
                    "hold_avg_price": "110152.5",
                    "open_avg_price": "110152.5",
                    "close_avg_price": "0.0",
                    "liquidate_price": "100000.0",
                    "oim": "0.0",
                    "im": "0.0",
                    "hold_fee": "0.0",
                    "realised": "0.0",
                    "leverage": "10",
                    "margin_ratio": "0.1",
                    "create_ts": 1625247600000,
                    "update_ts": 1625247600000
                }
            ]
        """
        return self._get("position", Position)

    @property
    def balance(self) -> Balance:
        @property
        def balance(self) -> Balance:
            """账户余额数据

            Data structure:

            .. code:: python

                [
                    {
                        "currency": "USDT",            # 币种
                        "position_margin": 0.3052,     # 持仓保证金
                        "available_balance": 19.7284,  # 可用余额
                        "frozen_balance": 0,           # 冻结余额
                        "bonus": 0,                    # 奖励
                        "last_bonus": 0,               # 最后奖励
                        "wallet_balance": 20.0337      # 钱包余额
                    }
                ]
            """
            return self._get("balance", Balance)
        return self._get("balance", Balance)

# SpotBalance: 现货账户余额数据存储

class SpotBalance(DataStore):
    _KEYS = ["currency"]

    def _fmt(self, balance: dict) -> dict:
        return {
            "currency": balance.get("currency"),
            "available": balance.get("available"),
            "frozen": balance.get("frozen"),
            "amount": balance.get("amount"),
            "avg_price": balance.get("avgPrice"),
        }

    def _fmt_ws(self, balance: dict) -> dict:
        return {
            "currency": balance.get("s"),
            "available": balance.get("av"),
            "frozen": balance.get("fr"),
            "amount": balance.get("to"),
            "avg_price": balance.get("ap"),
        }

    def _onresponse(self, data: dict[str, Any]):
        balances = data.get("data", [])
        items = [self._fmt(b) for b in balances]
        if items:
            self._clear()
            self._insert(items)

    def _on_message(self, msg: dict[str, Any]) -> None:
        data = msg.get("d", {})
        item = self._fmt_ws(data)
        self._update([item])


# SpotOrders: 现货订单数据存储
class SpotOrders(DataStore):
    _KEYS = ["order_id"]


    def _fmt(self, order: dict) -> dict:
        state = order.get("state")
        if state == 1 or state == 2:
            state = "open"
        elif state == 3:
            state = "filled"
        elif state == 4:
            state = "canceled"

        return {
            "order_id": order.get("id"),
            "symbol": order.get("symbol"),
            "currency": order.get("currency"),
            "market": order.get("market"),
            "trade_type": order.get("tradeType"),
            "order_type": order.get("orderType"),
            "price": order.get("price"),
            "quantity": order.get("quantity"),
            "amount": order.get("amount"),
            "deal_quantity": order.get("dealQuantity"),
            "deal_amount": order.get("dealAmount"),
            "avg_price": order.get("avgPrice"),
            "state": order.get("state"),
            "source": order.get("source"),
            "fee": order.get("fee"),
            "create_ts": order.get("createTime"),
            "unique_id": order.get("uniqueId"),
        }
    


    def _onresponse(self, data: dict[str, Any]):
        orders = (data.get("data") or {}).get("resultList", [])
        items = [self._fmt(order) for order in orders]
        self._clear()
        if items:
            self._insert(items)

    def _on_message(self, msg: dict[str, Any]) -> None:
        d:dict = msg.get("d", {})

        
        item = {
            "order_id": d.get("id"),
            "symbol": msg.get("s") or d.get("symbol"),
            "trade_type": d.get("tradeType"),
            "order_type": d.get("orderType"),
            "price": d.get("price"),
            "quantity": d.get("quantity"),
            "amount": d.get("amount"),
            "remain_quantity": d.get("remainQ"),
            "remain_amount": d.get("remainA"),
            "state": d.get("status"),
            "client_order_id": d.get("clientOrderId"),
            "is_taker": d.get("isTaker"),
            "create_ts": d.get("createTime"),
            "source": d.get("internal"),
        }

        state = d.get("status")

        if state == 2 or state == 1:
            item["state"] = "open"
            self._insert([item])
        
        elif state == 3:
            item["state"] = "filled"

            # 如果这三个字段存在追加
            if d.get("singleDealId") and d.get("singleDealPrice") and d.get("singleDealQuantity"):
                item.update({
                    "unique_id": d.get("singleDealId"),
                    "avg_price": d.get("singleDealPrice"),
                    "deal_quantity": d.get("singleDealQuantity"),
                })

                self._update([item])
                self._find_and_delete({  "order_id": d.get("id")  })
        
        elif state == 4:
            item["state"] = "canceled"
            self._update([item])
            self._find_and_delete({  "order_id": d.get("id")  })



class SpotBook(DataStore):
    _KEYS = ["s", "S", 'p']

    def _init(self) -> None:
        # super().__init__()
        self._time: int | None = None
        self.limit = 1

    def _onresponse(self, data: dict[str, Any]):

        top = data.get("data") or data.get("d") or data
        symbol = (
            top.get("s")
            or top.get("symbol")
            or (top.get("data") or {}).get("symbol")
        )

        inner = top.get("data") or top
        asks = inner.get("asks") or []
        bids = inner.get("bids") or []

        items: list[Item] = []
        if symbol:
            # Snapshot semantics: rebuild entries for this symbol
            self._find_and_delete({"s": symbol})

        def extract_pq(level: Any) -> tuple[Any, Any] | None:
            # Accept dict {"p": x, "q": y} or list/tuple [p, q, ...]
            if isinstance(level, dict):
                p = level.get("p")
                q = level.get("q")
                return (p, q)
            if isinstance(level, (list, tuple)) and len(level) >= 2:
                return (level[0], level[1])
            return None

        for side, S in ((asks, "a"), (bids, "b")):
            for level in side:
                pq = extract_pq(level)
                if not pq:
                    continue
                p, q = pq
                if p is None or q is None:
                    continue
                try:
                    if float(q) == 0.0:
                        continue
                except (TypeError, ValueError):
                    continue
                items.append({"s": symbol, "S": S, "p": p, "q": q})

        if items:
            self._insert(items)
    
        sort_data = self.sorted({'s': symbol}, self.limit)
        asks = sort_data.get('a', [])
        bids = sort_data.get('b', [])
        self._clear()
        self._update(asks + bids)
        


    def _on_message(self, msg: dict[str, Any]) -> None:
        ts = time.time() * 1000  # 预留时间戳（如需记录可用）
        data   = msg.get("d", {}) or {}
        symbol = msg.get("s")

        asks: list = data.get("asks", []) or []
        bids: list = data.get("bids", []) or []

        to_delete, to_update = [], []
        for side, S in ((asks, "a"), (bids, "b")):
            for item in side:
                if float(item["q"]) == 0.0:
                    to_delete.append({"s": symbol, "S": S, "p": item["p"]})
                else:
                    to_update.append({"s": symbol, "S": S, "p": item["p"], "q": item["q"]})
        
        self._delete(to_delete)
        self._insert(to_update)

        sort_data = self.sorted({'s': symbol}, self.limit)
        asks = sort_data.get('a', [])
        bids = sort_data.get('b', [])
        self._clear()
        self._update(asks + bids)

        # print(f'处理耗时: {time.time()*1000 - ts:.2f} ms')

    

    def sorted(
        self, query: Item | None = None, limit: int | None = None
    ) -> dict[str, list[Item]]:
        return self._sorted(
            item_key="S",
            item_asc_key="a",
            item_desc_key="b",
            sort_key="p",
            query=query,
            limit=limit,
        )

    @property
    def time(self) -> int | None:
        """返回最后更新时间"""
        return self._time



class SpotTicker(DataStore):
    _KEYS = ["symbol"]

    def _fmt(self, t: dict[str, Any]) -> dict[str, Any]:
        # 根据示例：
        # { id: "...", sb: "WCT_USDT", r8: "0.0094", tzr: "0.0094", c: "0.3002", h: "0.3035", l: "0.292", o: "0.2974", q: "1217506.41", a: "363548.8205" }
        return {
            "id": t.get("id"),
            "symbol": t.get("sb"),
            "last_price": t.get("c"),
            "open_price": t.get("o"),
            "high_price": t.get("h"),
            "low_price": t.get("l"),
            "volume24": t.get("q"),
            "amount24": t.get("a"),
            "rise_fall_rate": t.get("r8") if t.get("r8") is not None else t.get("tzr"),
        }

    def _onresponse(self, data: dict[str, Any] | list[dict[str, Any]]):
        # 支持 data 为:
        # - 直接为 list[dict]
        # - {"data": list[dict]}
        # - {"d": list[dict]}
        payload = data
        if isinstance(data, dict):
            payload = data.get("data") or data.get("d") or data
        if not isinstance(payload, list):
            payload = [payload]
        items = [self._fmt(t) for t in payload if isinstance(t, dict)]
        if not items:
            return
        self._clear()
        self._insert(items)

    def _on_message(self, msg: dict[str, Any]) -> None:
        # 兼容 WS:
        # { "c": "increase.tickers", "d": { ...ticker... } }
        d = msg.get("d") or msg.get("data") or msg
        if not isinstance(d, dict):
            return
        item = self._fmt(d)
        if not item.get("symbol"):
            return
        # 覆盖式更新该 symbol
        self._find_and_delete({"symbol": item["symbol"]})
        self._insert([item])

class SpotDetail(DataStore):
    _KEYS = ["name"]

    def _fmt(self, detail: dict) -> dict:
        return {
            "id": detail.get("id"),                    # 唯一ID
            "name": detail.get("vn"),          # 虚拟币简称
            "name_abbr": detail.get("vna"),    # 虚拟币全称
            "final_name": detail.get("fn"),            # 法币符号/展示名
            "sort": detail.get("srt"),                 # 排序字段
            "status": detail.get("sts"),               # 状态 (1=可用, 0=不可用)
            "type": detail.get("tp"),                  # 类型 (NEW=新币种)
            "internal_id": detail.get("in"),           # 内部唯一流水号
            "first_online_time": detail.get("fot"),    # 首次上线时间
            "online_time": detail.get("ot"),           # 上线时间
            "coin_partition": detail.get("cp"),        # 所属交易区分类
            "price_scale": detail.get("ps"),           # 价格小数位数
            "quantity_scale": detail.get("qs"),        # 数量小数位数
            "contract_decimal_mode": detail.get("cdm"), # 合约精度模式
            "contract_address": detail.get("ca"),      # 代币合约地址
        }

    def _onresponse(self, data: dict[str, Any]):
        details = data.get("data", {}).get('USDT')
        if not details:
            return
        
        items = [self._fmt(detail) for detail in details]
        self._clear()
        self._insert(items)


class OurbitSpotDataStore(DataStoreCollection):
    """
    Ourbit DataStoreCollection Spot
    """
    def _init(self) -> None:
        self._create("book", datastore_class=SpotBook)
        self._create("ticker", datastore_class=SpotTicker)
        self._create("balance", datastore_class=SpotBalance)
        self._create("order", datastore_class=SpotOrders)
        self._create("detail", datastore_class=SpotDetail)

    @property
    def book(self) -> SpotBook:
        """
        获取现货订单簿
        .. code:: json
            [
                {
                    "s": "BTC_USDT",
                    "S": "a",
                    "p": "110152.5",
                    "q": "53539"
                }
            ]

        """
        return self._get("book")
    
    @property
    def ticker(self) -> SpotTicker:
        """
        获取现货 Ticker
        .. code:: json
            [
                {
                    "symbol": "WCT_USDT",
                    "last_price": "0.3002",
                    "open_price": "0.2974",
                    "high_price": "0.3035",
                    "low_price": "0.292",
                    "volume24": "1217506.41",
                    "amount24": "363548.8205",
                    "rise_fall_rate": "0.0094",
                    "id": "dc893d07ca8345008db4d874da726a15"
                }
            ]
        """
        return self._get("ticker")

    @property
    def balance(self) -> SpotBalance:
        """
        现货账户余额数据流

        Data structure:

        .. code:: python

            [
                {
                    "currency": "USDT",       # 币种
                    "available": "100.0",     # 可用余额
                    "frozen": "0.0",          # 冻结余额
                    "usdt_available": "100.0",# USDT 可用余额
                    "usdt_frozen": "0.0",     # USDT 冻结余额
                    "amount": "100.0",        # 总金额
                    "avg_price": "1.0",       # 平均价格
                    "last_price": "1.0",      # 最新价格
                    "hidden_small": False,    # 是否隐藏小额资产
                    "icon": ""                # 币种图标
                }
            ]
        """
        return self._get("balance", SpotBalance)
    
    @property
    def detail(self) -> SpotDetail:
        """
        现货交易对详情数据流

        Data structure:

        .. code:: python

            [
                {
                    "id": "3aada397655d44d69f4fc899b9c88531",        # 唯一ID
                    "name": "USD1",                         # 虚拟币简称
                    "name_abbr": "USD1",                    # 虚拟币全称
                    "final_name": "USD1",                           # 法币符号/展示名
                    "sort": 57,                                     # 排序字段
                    "status": 1,                                    # 状态 (1=可用, 0=不可用)
                    "type": "NEW",                                  # 类型 (NEW=新币种)
                    "internal_id": "F20250508113754813fb3qX9NPxRoNUF", # 内部唯一流水号
                    "first_online_time": 1746676200000,             # 首次上线时间
                    "online_time": 1746676200000,                   # 上线时间
                    "coin_partition": ["ob_trade_zone_defi"],       # 所属交易区分类
                    "price_scale": 4,                               # 价格小数位数
                    "quantity_scale": 2,                            # 数量小数位数
                    "contract_decimal_mode": 1,                     # 合约精度模式
                    "contract_address": "0x8d0D000Ee44948FC98c9B98A4FA4921476f08B0d" # 代币合约地址
                }
            ]
        """
        return self._get("detail", SpotDetail)
    
    @property
    def orders(self) -> SpotOrders:
        """
        现货订单数据流

        Data structure:

        .. code:: python

            [
                {
                    "order_id": "123456",      # 订单ID
                    "symbol": "BTC_USDT",      # 交易对
                    "currency": "USDT",        # 币种
                    "market": "BTC_USDT",      # 市场
                    "trade_type": "buy",       # 交易类型
                    "order_type": "limit",     # 订单类型
                    "price": "11000.0",        # 委托价格
                    "quantity": "0.01",        # 委托数量
                    "amount": "110.0",         # 委托金额
                    "deal_quantity": "0.01",   # 成交数量
                    "deal_amount": "110.0",    # 成交金额
                    "avg_price": "11000.0",    # 成交均价
                    "state": "open",           # 订单状态
                    "source": "api",           # 来源
                    "fee": "0.01",             # 手续费
                    "create_ts": 1625247600000,# 创建时间戳
                    "unique_id": "abcdefg"     # 唯一标识
                }
            ]
        """
        return self._get("order", SpotOrders)
    
    def onmessage(self, msg: Item, ws: ClientWebSocketResponse | None = None) -> None:
        channel = msg.get("c")
 
        if channel is None:
            return
        if 'increase.aggre.depth' in channel:
            self.book._on_message(msg)

        if 'spot@private.orders' in channel:
            self.orders._on_message(msg)
        
        if 'spot@private.balances' in channel:
            self.balance._on_message(msg)

        if 'ticker' in channel:
            self.ticker._on_message(msg)

    async def initialize(self, *aws: Awaitable[aiohttp.ClientResponse]) -> None:
        """Initialize DataStore from HTTP response data."""
        for f in asyncio.as_completed(aws):
            res = await f
            data = await res.json()
            if res.url.path == "/api/platform/spot/market/depth":
                self.book._onresponse(data)
            if res.url.path == "/api/platform/spot/market/v2/tickers":
                self.ticker._onresponse(data)
            if res.url.path == "/api/assetbussiness/asset/spot/statistic":
                self.balance._onresponse(data)
            if res.url.path == "/api/platform/spot/order/current/orders/v2":
                self.orders._onresponse(data)
            if res.url.path == "/api/platform/spot/market/v2/symbols":
                self.detail._onresponse(data)