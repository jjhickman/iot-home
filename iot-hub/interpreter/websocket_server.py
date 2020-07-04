import asyncio
import json
import logging
import websockets
from human_detector import HumanDetector
from websockets import WebSocketServerProtocol

class WebSocketServer:
    def __init__(self, configuration):
        self.clients = set()
        self.configuration = configuration

    async def register(self, ws: WebSocketServerProtocol) -> None:
        self.clients.add(ws)
        logging.info(f'{ws.remote_address} connects')

    async def unregister(self, ws: WebSocketServerProtocol) -> None:
        self.clients.remove(ws)
        logging.info(f'{ws.remote_address} disconnects.')

    async def send_to_clients(self, message: str) -> None:
        if self.clients:
            await asyncio.wait([client.send(message) for client in self.clients])

    async def handler(self, ws: WebSocketServerProtocol, url: str) -> None:
        await self.register(ws)
        try:
            async for message in ws:
                notification = json.loads(message)
                if notification['topic'] == 'detect_human':
                    print('DETECTING HUMAN...')
                    duration_sec = 30
                    if notification['data']['camera_url'] != None:
                        self.configuration['camera_stream_url'] = notification['data']['camera_url']
                    if notification['data']['duration_seconds'] != None:
                        duration_sec = int(notification['data']['duration_seconds'])
                    detector = HumanDetector(self.configuration)
                    detector.detect(duration_sec)
        finally:
            await self.unregister(ws)

    async def distribute(self, ws: WebSocketServerProtocol) -> None:
        async for message in ws:
            await self.send_to_clients(message)
