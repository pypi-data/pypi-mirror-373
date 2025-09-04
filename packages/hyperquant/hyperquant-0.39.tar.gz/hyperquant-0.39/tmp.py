import asyncio
import random
import time
import pybotters
import hyperquant
from hyperquant.broker.models.ourbit import OurbitSpotDataStore
from hyperquant.broker.ourbit import OurbitSpot


async def main():
    store = OurbitSpotDataStore()

    async with pybotters.Client(
        apis={
            "ourbit": [
                "WEB3bf088f8b2f2fae07592fe1a6240e2d798100a9cb2a91f8fda1056b6865ab3ee"
            ]
        }
    ) as client:
        res = await client.fetch("POST", "https://www.ourbit.com/ucenter/api/user_info")

        ob_spot = OurbitSpot(client)
        await ob_spot.__aenter__()
        await ob_spot.sub_personal()
        await ob_spot.update('ticker')
        print(ob_spot.store.ticker.find())

        # while True:
        #     await ob_spot.store.balance.wait()
        #     print(ob_spot.store.balance.find())
        return

        await store.initialize(
            client.get("https://www.ourbit.com/api/platform/spot/market/v2/tickers")
        )

        print(store.ticker.find())

        return

        await store.initialize(
            client.get(
                "https://www.ourbit.com/api/platform/spot/market/depth?symbol=XRP_USDT"
            )
        )

        print(store.book.find())

        client.ws_connect(
            "wss://www.ourbit.com/ws?platform=web",
            send_json={
                "method": "SUBSCRIPTION",
                "params": ["spot@public.increase.aggre.depth@XRP_USDT"],
                "id": 3,
            },
            hdlr_json=store.onmessage,
        )
        while True:
            await store.book.wait()
            # await asyncio.sleep(1)
            print(store.book.find())
            # print(store.book.find({'s': 'XRP_USDT', 'S': 'a'}))
            # print(store.book.find({'s': 'XRP_USDT', 'S': 'b' }))
            # print(store.book.find())
            # ts = time.time()*1000
            # book = store.book.sorted({'s': 'XRP_USDT'}, 1)
            # print(f'排序耗时: {time.time()*1000 - ts:.2f} ms')


if __name__ == "__main__":
    asyncio.run(main())

# import aiohttp
# import asyncio

# async def fetch_orders():
#     url = "https://www.ourbit.com/api/platform/spot/order/current/orders/v2"
#     params = {
#         "orderTypes": "1,2,3,4,5,100",
#         "pageNum": "1",
#         "pageSize": "100",
#         "states": "0,1,3"
#     }
#     headers = {
#         "accept": "*/*",
#         "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
#         "baggage": "sentry-environment=prd,sentry-release=production%20-%20v3.28.8%20-%20cc4977f,sentry-public_key=48c007e1b13c063127c3119a97a2dd0e,sentry-trace_id=20b4bba185e143428bce7e3aeb376b63,sentry-sample_rate=0.1,sentry-sampled=true",
#         "cache-control": "no-cache",
#         "language": "zh-CN",
#         "luminex-trace-id": "0a4def65-f9ed-47df-8d72-7574abac2ae8-0100",
#         "luminex-uid": "31204775",
#         "pragma": "akamai-x-cache-on",
#         "priority": "u=1, i",
#         "referer": "https://www.ourbit.com/zh-CN/exchange/BTC_USDT",
#         "sec-ch-ua": '"Not;A=Brand";v="99", "Microsoft Edge";v="139", "Chromium";v="139"',
#         "sec-ch-ua-mobile": "?0",
#         "sec-ch-ua-platform": '"macOS"',
#         "sec-fetch-dest": "empty",
#         "sec-fetch-mode": "cors",
#         "sec-fetch-site": "same-origin",
#         "sentry-trace": "20b4bba185e143428bce7e3aeb376b63-99fc208a301b8675-1",
#         "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0"
#     }
#     cookies = {
#         "uc_token": "WEB3bf088f8b2f2fae07592fe1a6240e2d798100a9cb2a91f8fda1056b6865ab3ee",
#         "u_id": "WEB3bf088f8b2f2fae07592fe1a6240e2d798100a9cb2a91f8fda1056b6865ab3ee",
#     }

#     async with aiohttp.ClientSession(headers=headers, cookies=cookies) as session:
#         async with session.get(url, params=params) as resp:
#             data = await resp.json()
#             print(data)

# if __name__ == "__main__":
#     asyncio.run(fetch_orders())
