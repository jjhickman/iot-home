import json
import asyncio
import websockets

async def produce(message: str, host: str, port: int) -> None:
   async with websockets.connect(f'ws://{host}:{port}') as ws:
        await ws.send(message)
        print(f'> {message}')
        greeting = await ws.recv()
        print(f'< {greeting}')

notification = {'topic': 'detect_human', 'data': {'camera_url': 'http://blackberry:8000/stream.mjpg', 'duration_seconds': 30}}
asyncio.get_event_loop().run_until_complete(produce(json.dumps(notification), 'localhost', 4000))

