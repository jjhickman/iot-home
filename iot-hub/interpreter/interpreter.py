import pika
import sys
import os
import datetime
import argparse
import logging
import socketio
import collections
import math
import async_timeout
import asyncio
from io import BytesIO
import base64
import common
import cv2
import socketio
import numpy as np
import json
import time
import re
from PIL import Image

JOBS = {
    'person_detection': {
        'model': 'mobilenet_ssd_v2_face_quant_postprocess_edgetpu.tflite'
    }
}
THRESHOLD = 0.4
TOP_K = 10

ConnectTime = time.time()
Interpreter = None
Result = {}
Object = collections.namedtuple('Object', ['id', 'score', 'bbox'])
sio = None
class BBox(collections.namedtuple('BBox', ['xmin', 'ymin', 'xmax', 'ymax'])):
    """Bounding box.
    Represents a rectangle which sides are either vertical or horizontal, parallel
    to the x or y axis.
    """
    __slots__ = ()

def get_output(interpreter, score_threshold, top_k, image_scale=1.0):
    """Returns list of detected objects."""
    boxes = common.output_tensor(interpreter, 0)
    class_ids = common.output_tensor(interpreter, 1)
    scores = common.output_tensor(interpreter, 2)
    count = int(common.output_tensor(interpreter, 3))

    def make(i):
        ymin, xmin, ymax, xmax = boxes[i]
        return Object(
            id=int(class_ids[i]),
            score=scores[i],
            bbox=BBox(xmin=np.maximum(0.0, xmin),
                      ymin=np.maximum(0.0, ymin),
                      xmax=np.minimum(1.0, xmax),
                      ymax=np.minimum(1.0, ymax)))

    return [make(i) for i in range(top_k) if scores[i] >= score_threshold]

def load_job(config, job):
    try:
        data = json.loads(job)
        source = data['source']
        job_type = data['job_type']
        logger.debug('Loading job for {} doing {}'.format(data['source'], data['job_type']))
        job_interpreter = common.make_interpreter(os.path.join(config['models'] , JOBS[job_type]['model']))
        job_interpreter.allocate_tensors()
        logger.debug('Loading job of type: {} with model {} using source {}'.format(job_type, JOBS[job_type]['model'], source))
        return job_type, job_interpreter, source
    except ValueError as e:
        logger.error('Failed parsing job: {}'.format(e))
        return '', None, ''

def process_webstream(config, source):
    global Result
    Result = {}
    sio = socketio.Client()
    try:
        with async_timeout(config['job-timeout']):
            @sio.event
            async def connect():
                logger.debug('Connected at {}! Processing stream...'.format(datetime.datetime.now()))
    
            @sio.event
            async def connect_error():
                logger.error("The connection failed!")

            @sio.on('image')
            async def on_image(message):
                global Interpreter, Result
                try:
                    image = Image.open(BytesIO(base64.b64decode(message['data'])))
                    common.set_input(Interpreter, image)
                    start = time.time()
                    await Interpreter.invoke()
                    end = time.time()
                    logger.debug('Interpreted image in {} ms'.format(1000*(end - start)))
                    objects = get_output(Interpreter, score_threshold=config['threshold'], top_k=config['top-k'])
                    if len(objects) > 0:
                        logger.info('Person detected!')
                        filepath = os.path.join(config['images'], '{}.jpg'.format(datetime.datetime.now()))
                        Result = {
                            'job_type': 'person_detection',
                            'message': 'FOUND',
                            'file': filepath
                        }
                        await image.save(filepath)
                        await sio.disconnect()
                except Exception as e:
                    logger.debug('Error parsing message from socketio server: {}'.format(e))
                    Result = {
                        'job_type': 'person_detection',
                        'message': 'INTERPRETER_ERROR: {}'.format(e)
                    }
                    await sio.disconnect()
            logger.debug('Connecting to {} at {}'.format(source, time.time()))
            sio.connect(source)
    except asyncio.TimeoutError as e:
        logger.debug('Disconnecting. Job expired: {}'.format(e))
        Result = {
            'job_type': 'person_detection',
            'message': 'TIMEOUT: {}'.format(e)
        }
        sio.disconnect()
    except Exception as e:
        logger.error('Exception processing stream: {}'.format(e))
        Result = {
            'job_type': 'person_detection',
            'message': 'EXCEPTION: {}'.format(e)
        }
        sio.disconnect()
    return Result

def run(config, channel):
    global Interpreter
    for method_frame, _, body in channel.consume(config['input-queue']):
        logger.info('New RabbitMQ message: {}'.format(body))
        job_type, Interpreter, source = load_job(config, body)
        if job_type == 'person_detection':
            result = process_webstream(config, source)
            try:
                channel.basic_publish(exchange='',
                    routing_key=config['output-queue'],
                    body=json.dumps(result))
                channel.basic_ack(method_frame.delivery_tag)
            except pika.exceptions.ConnectionClosed as e:
                logger.error('Error notifying job complete: {}'.format(e))
                return

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Tensorflow Lite Interpreter Service')
    parser.add_argument('--job-timeout', type=int, help='Max processing time for job in seconds', default=30)
    parser.add_argument('--rabbitmq-host', type=str, help='Hostname for RabbitMQ broker', default='localhost')
    parser.add_argument('--input-queue', type=str, help='Input queue for interpreter jobs', default='input_queue')
    parser.add_argument('--output-queue', type=str, help='Output queue for interpreter jobs', default='output_queue')
    parser.add_argument('--models', type=str, help='Directory for Tensorflow Lite models', default='./models')
    parser.add_argument('--images', type=str, help='Directory for Tensorflow Lite models', default='./images')
    parser.add_argument('--top-k', type=int, help='Top k number of identified anomalies of interest', default=10)
    parser.add_argument('--threshold', type=float, help='Confidence threshold for model(s)', default=0.4)
    parser.add_argument('--log-level', type=int, help='Debug level for logging', default=logging.DEBUG)
    parser.add_argument('--log-file', type=str, help='File to log to', default='interpreter.log')
    config = parser.parse_args()

    log_formatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
    logger = logging.getLogger('interpreter')
    logger.setLevel(config['log-level'])
    if os.path.isdir(os.path.dirname(config['log-file'])) == False:
        os.makedirs(os.path.dirname(config['log-file']), exist_ok = True)
    file_handler = logging.RotatingFileHandler(config['log-file'], maxBytes=5000000, backupCount=10)
    file_handler.setFormatter(log_formatter)
    logger.addHandler(file_handler)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    logger.addHandler(console_handler)

    if os.path.isdir(config['images']) == False:
        os.makedirs(config['images'], exist_ok = True)

    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=config['rabbitmq-host']))
        channel = connection.channel()
        channel.basic_qos(prefetch_count=1) # tell RabbitMQ not to give more than one message at a time

        run(config, channel) # main service loop

        requeued_messages = channel.cancel()
        logger.info('Requeued %i messages' % requeued_messages)
        connection.close()
    except pika.exceptions.AMQPConnectionError as e:
        logger.error('Error connecting to RabbitMQ service: {}. Exiting...'.format(e))
