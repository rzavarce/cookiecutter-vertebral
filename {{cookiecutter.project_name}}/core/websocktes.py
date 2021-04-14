import time
import aiohttp

import random


DATA = {
    "geometry": {
        "type": "Point",
        "coordinates": [
            94.09104284060695,
            10.652780698520301
        ]
    },
    "type": "Feature",
    "properties": {

    }
}


async def WebSocketsHandler(request: aiohttp.web.Request) \
        -> aiohttp.web.Response:

    print('Websocket connection starting')
    ws = aiohttp.web.WebSocketResponse()
    await ws.prepare(request)
    print('Websocket connection ready')

    for i in range(10):
        DATA['geometry']['coordinates'][0] = \
            DATA['geometry']['coordinates'][0] - random.randint(1, 9)
        DATA['geometry']['coordinates'][1] = \
            DATA['geometry']['coordinates'][1] - random.randint(1, 9)
        await ws.send_json(DATA)
        time.sleep(2)

    print(random.randint(1, 9))

    await ws.send_json(DATA)
    async for msg in ws:
        print(msg)
        if msg.type == aiohttp.WSMsgType.TEXT:
            print(msg.data)
            if msg.data == 'close':
                await ws.close()
            else:

                await ws.send_str(msg.data + '/answer')
