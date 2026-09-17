import asyncio
import os
import websockets

viewers = set()

async def handler(websocket):
    if websocket.request.path == "/esp32":
        async for frame in websocket:
            if viewers:
                await asyncio.gather(
                    *(v.send(frame) for v in viewers),
                    return_exceptions=True
                )
    elif websocket.request.path == "/viewer":
        viewers.add(websocket)
        try:
            await websocket.wait_closed()
        finally:
            viewers.discard(websocket)

def process_request(connection, request):
    if request.path not in ("/esp32", "/viewer"):
        return connection.respond(200, "OK\n")
    return None

async def main():
    port = int(os.environ.get("PORT", 8765))
    async with websockets.serve(handler, "0.0.0.0", port, process_request=process_request):
        await asyncio.Future()

asyncio.run(main())
