import time
import sys
import argparse
import socket
import asyncio
import socketio
import netifaces as ni
import async_timeout
import cv2
import base64
import datetime
import functools
import logging
import pathlib
import RPi.GPIO as GPIO
import json
import aiohttp
from aiohttp import web
from middleware import setup_middlewares
http_logger = logging.getLogger('aiohttp.server')

awake_time = -1
cooldown_time = -1
stream_url = ''
sio = socketio.AsyncServer()

"""
=============================================================================
    REST API routes
=============================================================================
"""
# GET request handler for stream
async def index(request):
    index_html = """<html>
    <head><title>""" + socket.gethostname() + """</title></head>
        <body>
        <h1>""" + socket.gethostname() + """</h1>
        <img id='image' src=''/>
        <script src='https://cdnjs.cloudflare.com/ajax/libs/socket.io/1.7.4/socket.io.js'></script>
        <script>
            const socket = io.connect('""" + stream_url + """');
            socket.on('image', (image) => {
                let imageStr = new TextDecoder("utf-8").decode(image);
                document.getElementById('image').src = 'data:image/jpeg;base64,' + imageStr;
            });
        </script>
    </body>
    </html>"""
    logger.debug('Request for stream: {}\n\nSending: {}'.format(request, index_html))
    return web.Response(text=index_html, content_type='text/html')

# POST request handler for Hub notifications to ignore motion for a specified amount of time
async def sleep(request):
    global awake_time
    sleep_seconds = int(request.match_info.get('sleep_seconds', "1800"))
    if sleep_seconds > 0:
        awake_time = time.time() + sleep_seconds
        update = 'Sleeping for {} seconds, waking at {}'.format(sleep_seconds, time.ctime(awake_time))
        logger.debug(update)
        return web.Response(text=update)
    return web.Response(status=404, text='Invalid number of seconds in request: {}'.format(sleep_seconds))


"""
=============================================================================
    Motion detection via infrared GPIO and notification for hub
=============================================================================
"""
async def notify_hub(app, session):
    global stream_url
    try:
        with async_timeout.timeout(5):
            async with session.post(app['config']['hub-url'], data=stream_url) as response:
                return await response.status, response.text()
    except Exception as err:
        return 500, err

async def on_motion(app):
    global awake_time, cooldown_time
    epoch_time = time.time()
    if epoch_time > cooldown_time and epoch_time > awake_time:
        logger.info('Notifying hub at {}'.format(app['config']['hub-url']))
        cooldown_time = epoch_time + int(app['config']['cooldown-seconds'])
        async with aiohttp.ClientSession() as session:
            status, response = await notify_hub(app, session)
            if status != 200:
                logger.error('Failed notifying hub of motion detected! Code: {} Response: {}'.format(status, response))
            else:
                logger.info('Successfully notified hub of motion detected')

"""
=============================================================================
    SocketIO camera capture async loop for web stream and for GPIO input
=============================================================================
"""
async def stream(app):
    refresh_ms = 1.0 / int(app['config']['stream-fps'])
    logger.debug('Updating stream every {} ms'.format(refresh_ms))
    try:
        while True:
            ret, frame = app['capture'].read()
            if ret == False:
                http_logger.info("FAILED READING FROM CAPTURE")
                break
            ret, jpg_image = cv2.imencode('.jpg', frame)
            base64_image = base64.b64encode(jpg_image)
            await app['socket'].emit('image', base64_image)
            await asyncio.sleep(refresh_ms)
        logger.debug('Ended stream!')
    except asyncio.CancelledError:
        logger.debug('Stream cancelled')


async def monitor(app):
    pin = app['gpio_pin']
    while True:
        await asyncio.sleep(0.05)
        if GPIO.input(pin) > 0:
            logger.debug('Motion detected: {}'.format(pin))
            await on_motion(app)

"""
=============================================================================
    SocketIO handles
=============================================================================
"""
@sio.on('finished')
async def handle_finish(sid, data):
    print('Client {} finished job. Disconnecting...'.format(sid))
    await sio.disconnect(sid)

@sio.event
async def connect(sid, environ):
    print('CONNECTED to client with id: {}'.format(sid))

@sio.event
def disconnect(sid):
    print('DISCONNECTED from client with id: {}'.format(sid))


"""
=============================================================================
   Setup and configuration for GPIO, socketio, and web server/API
=============================================================================
"""
def initialize():
    global sio, stream_url

    wifi_address =  ni.ifaddresses('wlan0')[ni.AF_INET][0]['addr']

    parser = argparse.ArgumentParser(description='Raspberry Pi Infrared Security Camera')
    parser.add_argument('--gpio-pin', type=int, help='GPIO pin for infrared sensor signal', default=23)
    parser.add_argument('--stream-port', type=int, help='Port for camera stream', default=3000)
    parser.add_argument('--stream-fps', type=int, help='Frames per second for camera stream', default=24)
    parser.add_argument('--hub-url', type=str, help='Full URL for IoT hub REST API', default='http://192.168.50.110:8881')
    parser.add_argument('--cooldown-seconds', type=int, help='Number of seconds after notifying hub that it can repeat', default=30)
    parser.add_argument('--log-level', type=int, help='Debug level for logging', default=logging.DEBUG)
    parser.add_argument('--log-file', type=str, help='File to log to', default='picam_' + wifi_address + '.log')
    args = parser.parse_args()

    log_formatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
    logger = logging.getLogger('security-picam')
    logger.setLevel(args['log-level'])
    if os.path.isdir(os.path.dirname(config['log-file'])) == False:
        os.makedirs(os.path.dirname(config['log-file']), exist_ok = True)
    file_handler = logging.RotatingFileHandler(args['log-file'], maxBytes=5000000, backupCount=10)
    file_handler.setFormatter(log_formatter)
    logger.addHandler(file_handler)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    logger.addHandler(console_handler)

    app = web.Application()
    app['config'] = args
    
    stream_url = 'http://{}:{}'.format(wifi_address, app['config']['stream-port'])

    sio.attach(app)
    app['socket'] = sio

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(int(app['config']['gpio-pin']), GPIO.IN)
    app['gpio_pin'] = app['config']['gpio-pin']

    app.router.add_get('/', index)
    app.router.add_post('/sleep/{sleep_seconds}', sleep)
    setup_middlewares(app)
    app.on_startup.append(start_tasks)
    app.on_cleanup.append(cleanup_tasks)
    return app, wifi_address

async def start_tasks(app):
    app['capture'] = cv2.VideoCapture(0)
    app['stream'] = app.loop.create_task(stream(app))
    app['gpio'] = app.loop.create_task(monitor(app))

async def cleanup_tasks(app):
    app['capture'].release()
    GPIO.cleanup()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    app, wifi_address = initialize()
    web.run_app(app, host=wifi_address, port=app['config']['stream-port'])