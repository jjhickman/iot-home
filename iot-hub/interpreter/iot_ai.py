"""IoT Hub Human Detector - Perform Object Detection through IoT Web Cameras"""
from __future__ import print_function
import sys
import json
import asyncio
import websockets
from websocket_server import WebSocketServer


def print_usage():
    """Print required arguments to run"""
    print(sys.argv)
    if len(sys.argv) < 2:
        print('python3 iot_ai.py <configuration JSON>')
    else:
        print('{} {} <configuration JSON>'.format(sys.argv[0], sys.argv[1]))

def main():
    """Initialize websocket server to begin handling requests"""
    if len(sys.argv) != 2:
        print_usage()
        return
    with open(sys.argv[1]) as fin:
        configuration = json.load(fin)
        if configuration['websocket_url'] != None and configuration['websocket_port'] != None:
            websocket_server = WebSocketServer(configuration)
            start_server = websockets.serve(websocket_server.handler, \
                    configuration['websocket_url'], int(configuration['websocket_port']))
            loop = asyncio.get_event_loop()
            loop.run_until_complete(start_server)
            loop.run_forever()
        else:
            print_usage()
            return

if __name__ == '__main__':
    main()
