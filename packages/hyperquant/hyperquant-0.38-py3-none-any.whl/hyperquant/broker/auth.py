import time
import hashlib
from typing import Any
from aiohttp import ClientWebSocketResponse
from multidict import CIMultiDict
from yarl import URL
import pybotters
import json as pyjson
from urllib.parse import urlencode


def md5_hex(s: str) -> str:
    return hashlib.md5(s.encode("utf-8")).hexdigest()


# 🔑 Ourbit 的鉴权函数
class Auth:
    @staticmethod
    def ourbit(args: tuple[str, URL], kwargs: dict[str, Any]) -> tuple[str, URL]:
        method: str = args[0]
        url: URL = args[1]
        data = kwargs.get("data") or {}
        headers: CIMultiDict = kwargs["headers"]

        # 从 session 里取 token
        session = kwargs["session"]
        token = session.__dict__["_apis"][pybotters.auth.Hosts.items[url.host].name][0]

        # 时间戳 & body
        now_ms = int(time.time() * 1000)
        raw_body_for_sign = (
            data
            if isinstance(data, str)
            else pyjson.dumps(data, separators=(",", ":"), ensure_ascii=False)
        )

        # 签名
        mid_hash = md5_hex(f"{token}{now_ms}")[7:]
        final_hash = md5_hex(f"{now_ms}{raw_body_for_sign}{mid_hash}")

        # 设置 headers
        headers.update(
            {
                "Authorization": token,
                "Language": "Chinese",
                "language": "Chinese",
                "Content-Type": "application/json",
                "x-ourbit-sign": final_hash,
                "x-ourbit-nonce": str(now_ms),
            }
        )

        # 更新 kwargs.body，保证发出去的与签名一致
        kwargs.update({"data": raw_body_for_sign})

        return args

    @staticmethod
    def ourbit_spot(args: tuple[str, URL], kwargs: dict[str, Any]) -> tuple[str, URL]:
        method: str = args[0]
        url: URL = args[1]
        data = kwargs.get("data") or {}
        headers: CIMultiDict = kwargs["headers"]

        # 从 session 里取 token
        session = kwargs["session"]
        token = session.__dict__["_apis"][pybotters.auth.Hosts.items[url.host].name][0]
        cookie = f"uc_token={token}; u_id={token}; "
        headers.update({"cookie": cookie})

        # wss消息增加参数
        # if headers.get("Upgrade") == "websocket":
        #     args = (method, url)
        #     # 拼接 token
        #     q = dict(url.query)
        #     q["token"] = token
        #     url = url.with_query(q)


        return args


pybotters.auth.Hosts.items["futures.ourbit.com"] = pybotters.auth.Item(
    "ourbit", Auth.ourbit
)
pybotters.auth.Hosts.items["www.ourbit.com"] = pybotters.auth.Item(
    "ourbit", Auth.ourbit_spot
)
