import time
import sys
import os
import ssl
from variables import Variables
import socket
import asyncio
import socketio
import cv2
import base64
import datetime
import functools
import logging
import pathlib
import json
from skimage.measure import compare_ssim
from async_timeout import timeout
import aiohttp
from aiohttp import web
from middleware import setup_middlewares

awake_time = -1
stream_url = ''
sio = socketio.AsyncServer()
logger = None
static_back = None

"""
=============================================================================
    REST API routes
=============================================================================
"""
# GET request handler for stream
async def index(request):
    global logger
    index_html = """<html>
    <head><title>""" + socket.gethostname() + """</title></head>
        <body>
        <h1>""" + socket.gethostname() + """</h1>
        <img id='image' src=''/>
        <script src="https://cdn.socket.io/3.1.1/socket.io.min.js" integrity="sha384-gDaozqUvc4HTgo8iZjwth73C6dDDeOJsAgpxBcMpZYztUfjHXpzrpdrHRdVp8ySO" crossorigin="anonymous"></script>
        <script>
            const socket = io.connect('""" + stream_url + """');
            console.log("Connection started")
            socket.on('image', (image) => {
                console.log("New image!");
                let imageStr = new TextDecoder("utf-8").decode(image);
                document.getElementById('image').src = 'data:image/jpeg;base64,' + imageStr;
            });
        </script>
    </body>
    </html>"""
    logger.debug('Request for stream: {}\n\nSending: {}'.format(request, index_html))
    return web.Response(text=index_html, content_type='text/html')

def motion_found(threshold, frame):
    global static_back
    motion = False

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0) 
    if static_back is None: 
        static_back = gray 
        return motion
    (score, diff) = compare_ssim(static_back, gray, full=True)
    diff = (diff * 255).astype("uint8")
    thresh = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    #diff_frame = cv2.absdiff(static_back, gray)
    #thresh_frame = cv2.threshold(diff_frame, threshold, 255, cv2.THRESH_BINARY)[1] 
    #thresh_frame = cv2.dilate(thresh_frame, None, iterations = 2) 
    #cnts, _ = cv2.findContours(thresh_frame.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) 
    cnts, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for contour in cnts: 
        if cv2.contourArea(contour) >= 5000:
            logger.debug("BIG AREA OF CHANGE: " + str(cv2.contourArea(contour)))
            motion = True
            (x, y, w, h) = cv2.boundingRect(contour)
    if motion == True:
        logger.debug("Motion detected")
    return motion


"""
=============================================================================
    SocketIO camera capture async loop for web stream and for GPIO input
=============================================================================
"""
async def stream(app):
    global logger, stream_url, awake_time
    refresh_seconds = 1.0 / int(app['config'].stream_fps)
    logger.debug('Updating stream every {} seconds'.format(refresh_seconds))
    try:
        while True:
            ret, frame = app['capture'].read()
            if ret == False:
                logger.error("FAILED READING FROM CAPTURE")
                break
            ret, jpg_image = cv2.imencode('.jpg', frame)
            base64_image = base64.b64encode(jpg_image)
            await app['socket'].emit('image', base64_image)

            awake = time.time() >= awake_time
            if awake and motion_found(int(app['config'].threshold), frame):
                try:
                    async with timeout(5):
                        async with aiohttp.ClientSession() as session:
                            try:
                                async with session.post(app['config'].hub_url, auth=aiohttp.BasicAuth(app['config'].hub_username, app['config'].hub_password,'utf-8'), json={'source': stream_url, 'time': round(time.time() * 1000)}) as response:
                                    status = await response.status()
                                    data = await response.json()
                                    if status != 200:
                                        logger.error("Status: " + str(status) + " - sleeping for default 60 seconds...")
                                        awake_time = time.time() + 60
                                    else:
                                        if data['sleep_seconds'] and int(data['sleep_seconds']) > 0:
                                            awake_time = time.time() + int(data['sleep_seconds'])
                                            logger.info("Sleeping for " + str(data['sleep_seconds']) + " seconds...")
                                        else:
                                            awake_time = time.time() +  60
                                            logger.error("No sleep_seconds field in JSON response. Sleeping for default 60 seconds...")
                            except aiohttp.ClientError as e:
                                await asyncio.sleep(refresh_seconds)
                                logger.error("HTTP Client POST error: " + str(e))
                                awake_time = time.time() + 60
                except asyncio.TimeoutError:
                    await asyncio.sleep(refresh_seconds)
                    logger.debug("Timed out trying to make request to hub")
            await asyncio.sleep(refresh_seconds)
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
    logger.info('Client {} finished job. Disconnecting...'.format(sid))
    await sio.disconnect(sid)

@sio.event
async def connect(sid, environ):
    logger.info('CONNECTED to client with id: {}'.format(sid))

@sio.event
def disconnect(sid):
    logger.info('DISCONNECTED from client with id: {}'.format(sid))


"""
=============================================================================
   Setup and configuration for GPIO, socketio, and web server/API
=============================================================================
"""
def initialize():
    global sio, stream_url, logger

    args = Variables()

    log_formatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
    logger = logging.getLogger('aiohttp.server')
    logger.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    logger.addHandler(console_handler)

    app = web.Application()
    app['config'] = args
    
    stream_url = 'http://{}:{}'.format(app['config'].address, app['config'].stream_port)

    sio.attach(app)
    app['socket'] = sio

    app.router.add_get('/', index)
    setup_middlewares(app)
    app.on_startup.append(start_tasks)
    app.on_cleanup.append(cleanup_tasks)
    return app, app['config'].address

async def start_tasks(app):
    app['capture'] = cv2.VideoCapture(0)
    app['stream'] = app.loop.create_task(stream(app))

async def cleanup_tasks(app):
    app['capture'].release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    app, address = initialize()
    web.run_app(app, host="0.0.0.0", port=app['config'].stream_port)
