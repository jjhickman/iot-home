import pika
import sys
import os
from variables import Variables
import datetime
import argparse
import logging
import logging.handlers
import socket
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
        job_interpreter = common.make_interpreter(os.path.join(config.models , JOBS[job_type]['model']))
        job_interpreter.allocate_tensors()
        logger.debug('Loading job of type: {} with model {} using source {}'.format(job_type, JOBS[job_type]['model'], source))
        return job_type, job_interpreter, source
    except ValueError as e:
        logger.error('Failed parsing job: {}'.format(e))
        return '', None, ''
    except KeyError as e:
        logger.error('Failed parsing job: {}'.format(e))
        return '', None, ''

def process_webstream(config, source):
    global Result
    Result = {}
    sio = socketio.Client()
    try:
        with async_timeout(config.job_timeout):
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
                    objects = get_output(Interpreter, score_threshold=config.threshold, top_k=config.top_k)
                    if len(objects) > 0:
                        logger.info('Person detected!')
                        filepath = os.path.join(config.images, '{}.jpg'.format(datetime.datetime.now()))
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
    return Result

def run(config, channel):
    global Interpreter
    for method_frame, _, body in channel.consume(config.input_queue):
        logger.info('New RabbitMQ message: {}'.format(body))
        try:
            job_type, Interpreter, source = load_job(config, body)
            if job_type == 'person_detection':
                result = process_webstream(config, source)
                channel.basic_publish(exchange='',
                    routing_key=config.output_queue,
                    body=json.dumps(result))
            channel.basic_ack(method_frame.delivery_tag)
        except pika.exceptions.ConnectionClosed as e:
            logger.error('Error notifying job complete: {}'.format(e))
            return

if __name__ == '__main__':

    config = Variables()
    log_formatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
    logger = logging.getLogger('interpreter')
    logger.setLevel(config.log_level)
    if os.path.isdir(os.path.dirname(config.log_dir)) == False:
        os.makedirs(os.path.dirname(config.log_dir), exist_ok = True)
    
    file_handler = logging.handlers.RotatingFileHandler(os.path.join(config.log_dir, '{}.log'.format(socket.gethostname())), maxBytes=5000000, backupCount=10)
    file_handler.setFormatter(log_formatter)
    logger.addHandler(file_handler)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    logger.addHandler(console_handler)

    if os.path.isdir(config.images) == False:
        os.makedirs(config.images, exist_ok = True)

    try:
        credentials = pika.PlainCredentials(config.rabbitmq_user, config.rabbitmq_password)
        parameters = pika.ConnectionParameters(host=config.rabbitmq_host, credentials=credentials)
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        channel.basic_qos(prefetch_count=1) # tell RabbitMQ not to give more than one message at a time

        run(config, channel) # main service loop

        requeued_messages = channel.cancel()
        logger.info('Requeued %i messages' % requeued_messages)
        connection.close()
    except pika.exceptions.AMQPConnectionError as e:
        logger.error('Error connecting to RabbitMQ service: {}. Exiting...'.format(e))