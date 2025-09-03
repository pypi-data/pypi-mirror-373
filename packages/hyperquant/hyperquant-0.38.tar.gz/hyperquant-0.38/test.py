# import asyncio
# import hyperquant
# from hyperquant.broker.models.ourbit import OurbitSwapDataStore
# import pybotters

# async def test():
#     store = OurbitSwapDataStore()
#     async with pybotters.Client(
#         apis={
#             "ourbit": [
#                 "WEB3bf088f8b2f2fae07592fe1a6240e2d798100a9cb2a91f8fda1056b6865ab3ee"
#             ]
#         }
#     ) as client:
#         await store.initialize( client.get( "https://futures.ourbit.com/api/v1/private/position/open_positions") )
#         print(store.position.find())

# if __name__ == "__main__":
#     asyncio.run(test())

import asyncio
from hyperquant.broker.ourbit import OurbitSwap
import pybotters
import hyperquant

async def test():
    async with pybotters.Client(
        apis={
            "ourbit": [
                "WEB3bf088f8b2f2fae07592fe1a6240e2d798100a9cb2a91f8fda1056b6865ab3ee"
            ]
        }
    ) as client:
        ourbit = OurbitSwap(client)
        await ourbit.__aenter__()
        res = await ourbit.place_order(
            symbol="SOL_USDT",
            size=1,
            side="buy",
            order_type="limit_GTC",
            price=192
        )
        print(res)

        
        # # await ourbit.update('orders')
        # await ourbit.sub_personal()

        # while True:
        #     await ourbit.store.position.wait()
        #     print(ourbit.store.position.find())
        #     # await ourbit.store.position.wait()
        #     # print(ourbit.store.position.find())
        #     await ourbit.store.orders.wait()
        
        # with ourbit.store.orders.watch() as changes:
        #     async for change in changes:
        #         print(change.operation, change.data)


        # print(res.data)

        # print(ourbit.datastore.detail.find({"symbol": "SOL_USDT"}))

        # print(ourbit.datastore.detail.find())

        # await ourbit.update('balance')
        # print(ourbit.store.balance.find())

        # res = await client.fetch(
        #     'GET',
        #     'https://futures.ourbit.com//api/v1/private/order/list/history_orders?category=1&page_num=1&page_size=4&start_time=1755682343814&states=4&symbol=SOL_USDT'
        # )

        # print(res.data)

        # print(await ourbit.query_order('219079365441409152'))

        # await ourbit.place_order(
        #     symbol="SOL_USDT",
        #     side="sell",
        #     order_type="market",
        #     usdt_amount=3,
        #     price=206.44
        # )

        # print(ourbit.datastore.orders.find())

        # await ourbit.cancel_orders(['219206341921656960'])


        # print(ourbit.datastore.orders.find())

        # ps = ourbit.datastore.position.find({
        #     "symbol": "SOL_USDT",
        #     "side": "long"
        # })[0]

        # position_id = ps.get("position_id")

        # await ourbit.place_order(
        #     symbol="SOL_USDT",
        #     size=1,
        #     side="close",
        #     order_type="market",
        #     position_id=position_id
        # )

        # await ourbit.sub_order_book("SOL_USDT")

        # while True:
        #     await ourbit.store.book.wait()
        #     asks = ourbit.store.book.find({'side': 'A'})
        #     bids = ourbit.store.book.find({'side': 'B'})
        #     print("Ask0:", asks[0]['px'])
        #     print("Bid0:", bids[0]['px'])
        #     print('-----\n')

if __name__ == "__main__":
    asyncio.run(test())