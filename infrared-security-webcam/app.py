import time
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
logger = logging.getLogger('aiohttp.server')

awake_time = -1
cooldown_time = -1
stream_url = ''
sio = None

"""
=============================================================================
    REST API routes
=============================================================================
"""
# GET request handler for stream
async def index(request):
    index_html = """<html>
    <head><title>""" + stream_url + """</title></head>
        <body>
        <h1>""" + stream_url + """</h1>
        <img id='image' src=''/>
        <script src='https://cdnjs.cloudflare.com/ajax/libs/socket.io/1.7.4/socket.io.js'></script>
        <script>
            const socket = io.connect('""" + stream_url + """');
            socket.on('image', (image) => {
                document.getElementById('image').src = 'data:image/jpeg;base64, ' + image;
                console.log(document.getElementById('image').src)
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
        logger.info(update)
        return web.Response(text=update)
    return web.Response(status=404, text='Invalid number of seconds in request: {}'.format(sleep_seconds))


"""
=============================================================================
    Motion detection via infrared GPIO and notification for hub
=============================================================================
"""
# Make 
async def notify_hub(app, session):
    global stream_url
    with async_timeout.timeout(app['config']['hub_wait_seconds']):
        async with session.post(app['config']['hub_url'], data=stream_url) as response:
            return await response.status, response.text() 

async def on_motion(pin):
    global awake_time, cooldown_time
    epoch_time = time.time()
    if epoch_time > cooldown_time and epoch_time > awake_time:
        logger.info('Motion detected!')
        cooldown_time = epoch_time + int(app['config']['cooldown_seconds'])
        async with aiohttp.ClientSession() as session:
            status, response = await notify_hub(app, session)
            if status != 200:
                logger.error('Failed notifying hub of motion detected! Code: {} Response: {}'.format(status, response))
            else:
                logger.info('Successfully notified hub of motion detected')

"""
=============================================================================
    SocketIO camera capture async loop for web stream
=============================================================================
"""
async def stream(app):
    global sio
    refresh_ms = 1.0 / int(app['config']['fps'])
    logger.debug('Updating stream every {} ms'.format(refresh_ms))
    try:
        while True:
            ret, frame = app['capture'].read()
            
            if ret == False:
                print("FAILED READING FROM CAPTURE")
                break
            ret, jpg_image = cv2.imencode('.jpg', frame)
            base64_image = base64.b64encode(jpg_image)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            await sio.emit('image', base64_image)
            await asyncio.sleep(refresh_ms)
        logger.debug('Ended stream!')
    except asyncio.CancelledError:
        logger.debug('Stream cancelled')

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
    config = None
    with open('./config.json') as f:
        config = json.load(f)
    app = web.Application()
    app['config'] = config
    
    wifi_address =  ni.ifaddresses('wlan0')[ni.AF_INET][0]['addr']
    stream_url = 'http://{}:{}'.format(wifi_address, app['config']['port'])

    sio = socketio.AsyncServer(logger=logger)
    sio.attach(app)

    # app['gpio'] = gpio
    #app['gpio_callback'] = app['gpio'].callback(app['config']['infrared_gpio'], pigpio.RISING_EDGE, on_motion)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(int(app['config']['infrared_gpio']), GPIO.IN)
    GPIO.add_event_detect(int(app['config']['infrared_gpio']), GPIO.RISING, callback=on_motion)

    app.router.add_get('/', index)
    app.router.add_post('/sleep/{sleep_seconds}', sleep)
    setup_middlewares(app)
    app.on_startup.append(start_tasks)
    app.on_cleanup.append(cleanup_tasks)
    return app, wifi_address

async def start_tasks(app):
    app['capture'] = cv2.VideoCapture(0)
    app['stream'] = app.loop.create_task(stream(app))

async def cleanup_tasks(app):
    app['capture'].release()
    GPIO.cleanup()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app, wifi_address = initialize()
    web.run_app(app, host=wifi_address, port=app['config']['port'])
