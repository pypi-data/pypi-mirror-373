from __future__ import annotations

import time
from aiohttp import ClientWebSocketResponse
import aiohttp

from pybotters.store import DataStore
from pybotters.models.hyperliquid import HyperliquidDataStore
from typing import TYPE_CHECKING, Awaitable

if TYPE_CHECKING:
    from pybotters.typedefs import Item
    from pybotters.ws import ClientWebSocketResponse



# {'channel': 'orderUpdates', 'data': [{'order': {'coin': 'HYPE', 'side': 'A', 'limitPx': '22.887', 'sz': '1.12', 'oid': 29641480516, 'timestamp': 1746766108031, 'origSz': '1.12', 'reduceOnly': True}, 'status': 'rejected', 'statusTimestamp': 1746766108031}]}
class OrderStore(DataStore):
    _KEYS = ["oid"]

    def _onmessage(self, msg: Item) -> None:

        for rec in msg:
            order = rec["order"]
            item = {
                **order,
                "status": rec.get("status"),
                "px": None,
                'fee': None,
                "statusTimestamp": rec.get("statusTimestamp"),
            }

            if item["status"] == "open":
                self._update([item])
            else:
                self._delete([item])

class FillStore(DataStore):
    _KEYS = ["oid"]

    def _onmessage(self, msg: Item) -> None:
        for fill in msg:
            self._update([fill])



class Account(DataStore):
    _KEYS = ["marginCoin", "value"]
     
    def _onmessage(self, data: list[Item]) -> None:
            self._update(
                [
                    {
                        "marginCoin": 'USDC',
                        'value': float(item['accountValue']),
                        'frozen': float(item['totalMarginUsed']),
                        'available': float(item['accountValue']) - float(item['totalMarginUsed']),
                    }
                    for item in data
                ]
            )

class SpotAccount(DataStore):

    _KEYS = ["coin"]

    def _onmessage(self, data: list[Item]) -> None:
        self._update(
            [
                {
                    "coin": item['coin'],
                    "total": float(item['total']),
                    "frozen": float(item['hold']),
                    "available": float(item['total']) - float(item['hold']),
                    "entryNtl": float(item['entryNtl']),
                }
                for item in data
            ]
        )

class PositionStore(DataStore):
    _KEYS = ["coin"]

    def _onmessage(self, data: list[Item]) -> None:
      
        if len(data) == 0 and self.__len__() > 0:
            self._clear()
        elif len(data) > 0:
            self._update([

                {
                    "coin": item['position']['coin'],
                    "sz": float(item['position']['szi']),
                    "px": float(item['position']['entryPx']),
                    'unpnl': float(item['position']['unrealizedPnl']),
                    'rt': float(item['position']['returnOnEquity']),
                    'lv': int(item['position']['leverage']['value']),
                }
                for item in data
            ])

        
class MyHyperStore(HyperliquidDataStore):
    ORDER_TYPE = 'orderUpdates'
    WEBDATA2_TYPE = 'webData2'
    ORDER_FILL_TYPE = 'userFills'

    def _init(self) -> None:
        self._create("orders", datastore_class=OrderStore)
        self._create("account", datastore_class=Account)
        self._create("positions", datastore_class=PositionStore)
        self._create("spot_account", datastore_class=SpotAccount)
        self._create("fills", datastore_class=FillStore)
        super()._init()

    def _onmessage(self, msg: Item, ws: ClientWebSocketResponse | None = None) -> None:

        if msg.get("channel") == self.ORDER_TYPE:
            self.orders._onmessage(msg.get('data', []))
        elif msg.get("channel") == self.WEBDATA2_TYPE:
            # print(msg.get('data', {}).get('clearinghouseState', {}))
            act_data = msg.get('data', {}).get('clearinghouseState', {}).get('crossMarginSummary', [])
            if act_data:
                self.account._onmessage([act_data])

            pos_data = msg.get('data', {}).get('clearinghouseState', {}).get('assetPositions', [])
            self.positions._onmessage(pos_data)

            spot_act_data = msg.get('data', {}).get('spotState', {}).get('balances', [])
            self.spot_account._onmessage(spot_act_data)

        elif msg.get("channel") == self.ORDER_FILL_TYPE:
            fills = msg.get('data', {}).get('fills', [])
            is_snap = msg.get('data', {}).get('isSnapshot', False)
            if not is_snap:
                self.fills._onmessage(fills)
  
        super()._onmessage(msg, ws)
            
    async def initialize(self, *aws: tuple[str, Awaitable[aiohttp.ClientResponse]]) -> None:

        for a in aws:
            method, f = a
            resp = await f
            data = await resp.json()
            if method == "orders":

                self.orders._onmessage(
                    [
                        {
                            'order': o,
                            'status': "open",
                            'statusTimestamp': int(time.time() * 1000)
                        } for o in data
                    ]
                )
            
        pass

    @property
    def orders(self) -> OrderStore:
        """``orders`` data stream.

        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/websocket/subscriptions

        Data structure:

        .. code:: python
            [
                {
                    "coin": "HYPE",
                    "side": "A",
                    "limitPx": "22.887",
                    "sz": "1.12",
                    "oid": 29641480516,
                    "timestamp": 1746766108031,
                    "origSz": "1.12",
                    "reduceOnly": True
                    "status": "open",
                    "statusTimestamp": 1746766108031
                }...
            ]
        """
        return self._get("orders", OrderStore)
    @property
    def account(self) -> Account:
        """``account`` data stream.
        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/websocket/subscriptions
        Data structure:
        .. code:: python
            [
                {
                    "marginCoin": 'USDC',
                    'value': float(item['accountValue']),
                    'frozen': float(item['totalMarginUsed']),
                    'available': float(item['accountValue']) - float(item['totalMarginUsed']),
                }...
            ]
        """
        return self._get("account", Account)
    
    @property
    def positions(self) -> PositionStore:
        return self._get("positions", PositionStore)
    
    @property
    def spot_account(self) -> SpotAccount:
        """``spot_account`` data stream.
        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/websocket/subscriptions
        Data structure:
        .. code:: python
            [
                {
                    "coin": 'FEUSD',
                    "sz": "21.0",
                    "px": "0.9719",
                    "unpnl": "0.0",
                    "rt": "0.0",
                    "lv": 1,
                }...
            ]
        """
        return self._get("spot_account", SpotAccount)
   
    @property
    def fills(self) -> FillStore:
        """``fills`` data stream.
        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/websocket/subscriptions
        Data structure:
        .. code:: python
            [
                {
                    "coin": 'FEUSD',
                    "px": "0.9719",
                    "sz": "21.0",
                    "side": 'buy',
                    "time": 1679999999999,
                    "startPosition": '0.0',
                    "dir": 'buy',
                    "closedPnl": '0.0',
                    "hash": '0x123456789abcdef',
                    "oid": 123456789,
                    "crossed": True,
                    "fee": '-0.0001',
                    "tid": 987654321,
                    "liquidation": None,
                    "feeToken": 'USDC',
                }...
            ]
        """
        return self._get("fills", FillStore)

