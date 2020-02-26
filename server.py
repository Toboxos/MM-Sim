import asyncio
from aioconsole import ainput
import websockets
import json
import threading

msg_out = { 'msg': 'out', 'angle': 0.0 }

sockets = []
async def hello(websocket, path):
    #print( "New socket" )
    sockets.append( websocket )
    async for message in websocket:
        pass

async def check():
    while True:
        i = await ainput("angle:")
        msg_out['angle'] = float( i )

        for s in sockets:
            if s.closed:
                continue
            await s.send( json.dumps(msg_out) )


threading.Thread(target=check).start()
server = websockets.serve(hello, "localhost", 8080)
asyncio.get_event_loop().run_until_complete(server)
asyncio.get_event_loop().run_until_complete(check())
asyncio.get_event_loop().run_forever()
