import pika
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
        job_interpreter = common.make_interpreter(config['model_directory'] + '/' + JOBS[job_type]['model'])
        job_interpreter.allocate_tensors()
        print('Loading job of type: {} with model {} using source {}'.format(job_type, JOBS[job_type]['model'], source))
        return job_type, job_interpreter, source
    except ValueError:
        print('Failed parsing job')
        return '', None, ''

def process_webstream(source):
    global Result, ConnectTime
    Result = {}
    sio = socketio.Client()
    try:
        async with async_timeout(30):
            @sio.event
            async def connect():
                global ConnectTime
                ConnectTime = time.time()
                print('Connected at {}! Processing stream...'.format(ConnectTime))
    
            @sio.event
            async def connect_error():
                print("The connection failed!")

            @sio.on('image')
            async def on_image(message):
                global Interpreter, Result
                try:
                    image = Image.open(BytesIO(base64.b64decode(message['data'])))
                    common.set_input(Interpreter, image, resample='Image.NEAREST')
                    start = time.time()
                    await Interpreter.invoke()
                    end = time.time()
                    print('Interpreted image in {} seconds'.format(end - start))
                    objects = get_output(Interpreter, score_threshold=THRESHOLD, top_k=TOP_K)
                    if len(objects) > 0:
                        print('Person detected!')
                        Result = {
                            'job_type': 'person_detection',
                            'message': 'FOUND'
                        }
                        await sio.disconnect()
                        return Result
                except Exception as err:
                    print('Error parsing message from socketio server: {}'.format(err))
                    Result = {
                        'job_type': 'person_detection',
                        'message': 'INTERPRETER_ERROR: {}'.format(err)
                    }
                    await sio.disconnect()
                    return Result
            print('Connecting to {} at {}'.format(source, time.time()))
            await sio.connect(source)
    except asyncio.TimeoutError as err:
        print('Disconnecting. Session expired: {}'.format(err))
        Result = {
            'job_type': 'person_detection',
            'message': 'TIMEOUT: {}'.format(err)
        }
        await sio.disconnect()
        return Result
    except Exception as err:
        Result = {
            'job_type': 'person_detection',
            'message': 'EXCEPTION: {}'.format(err)
        }
        await sio.disconnect()
        return Result

def run(config, channel):
    global Interpreter
    for method_frame, _, body in channel.consume(config['input_interpreter_queue']):
        print('New RabbitMQ message: {}'.format(body))
        job_type, Interpreter, source = load_job(config, body)
        if job_type == 'person_detection':
            Result = process_webstream(source)
            channel.basic_publish(exchange='',
                  routing_key=config['output_interpreter_queue'],
                  body=json.dumps(Result))
            channel.basic_ack(method_frame.delivery_tag)


if __name__ == '__main__':
    with open('./config.json') as contents:
        config = json.load(contents)
    print('Config: {}'.format(config))
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=config['rabbitmq_host']))
    channel = connection.channel()
    channel.basic_qos(prefetch_count=1) # tell RabbitMQ not to give more than one message at a time

    run(config, channel) # main service loop

    requeued_messages = channel.cancel()
    print('Requeued %i messages' % requeued_messages)
    connection.close()