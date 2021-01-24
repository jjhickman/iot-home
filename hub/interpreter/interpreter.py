
import argparse
import cv2
import pika
import socketio
import async_timeout
import asyncio
from PIL import Image
from io import BytesIO
import base64
import os
import json
import datetime
import time
import helper
from pycoral.adapters.detect import get_objects
from pycoral.utils.edgetpu import run_inference

sio = None
result = {}
logger = None

def process_webstream(args, interpreter, inference_size, source):
    global result,sio, logger
    result = {}
    sio = socketio.Client()
    try:
        with async_timeout(args.job_timeout):
            @sio.event
            async def connect():
                global logger
                logger.debug('Connected at {}! Processing stream...'.format(datetime.datetime.now()))
    
            @sio.event
            async def connect_error():
                global logger
                logger.error("The connection failed!")

            @sio.on('image')
            async def on_image(message):
                global result, sio, logger
                try:
                    #image = Image.open(BytesIO(base64.b64decode(message['data'])))
                    image = BytesIO(base64.b64decode(message['data']))
                    start = time.time()
                    run_inference(interpreter, image)
                    logger.debug('Interpreted image in {} ms'.format(1000*(time.time() - start)))
                    objects = get_objects(interpreter, args.threshold)[:args.top_k]
                    image = helper.append_objs_to_img(cv2_im, inference_size, objs, labels)
                    if len(objects) > 0:
                        logger.info('Person detected!')
                        filepath = os.path.join(args.output_dir, '{}.jpg'.format(datetime.datetime.now()))
                        result = {
                            'job_type': 'person_detection',
                            'message': 'FOUND',
                            'file': filepath
                        }
                        await image.save(filepath)
                        await sio.disconnect()
                except Exception as e:
                    logger.debug('Error parsing message from socketio server: {}'.format(e))
                    result = {
                        'job_type': 'person_detection',
                        'message': 'INTERPRETER_ERROR: {}'.format(e)
                    }
                    await sio.disconnect()
            logger.debug('Connecting to {} at {}'.format(source, time.time()))
            sio.connect(source)
    except asyncio.TimeoutError as e:
        logger.debug('Disconnecting. Job expired: {}'.format(e))
        result = {
            'job_type': 'person_detection',
            'message': 'TIMEOUT: {}'.format(e)
        }
        sio.disconnect()
    except Exception as e:
        logger.error('Exception processing stream: {}'.format(e))
        result = {
            'job_type': 'person_detection',
            'message': 'EXCEPTION: {}'.format(e)
        }
    return result

def run(args, channel, logger):
    interpreter, inference_size = helper.load_interpreter(os.path.join(args.model_dir, args.default_model), os.path.join(args.model_dir, args.default_labels))
    job_type = args.default_job_type
    for method_frame, _, body in channel.consume(args.input_queue):
        logger.info('New RabbitMQ message: {}'.format(body))
        try:
            job_type, interpreter, inference_size, source = load_job(args, current_job_type, interpreter, body)
            if job_type == 'person_detection':
                result = process_webstream(args, interpreter, inference_size, source)
                channel.basic_publish(exchange='',
                    routing_key=args.output_queue,
                    body=json.dumps(result))
            channel.basic_ack(method_frame.delivery_tag)
        except pika.exceptions.ConnectionClosed as e:
            logger.error('Error notifying job complete: {}'.format(e))
            return

def main():
    parser = argparse.ArgumentParser(description="Coral TPU camera stream interpreter service")
    parser.add_argument('--model_dir', help='.tflite model path',
                        default='./models/')
    parser.add_argument('--default_labels', help='label file path',
                        default='./models/coco_labels.txt')
    parser.add_argument('--default_model', help='label file path',
                        default='./models/mobilenet_ssd_v2_face_quant_postprocess_edgetpu.tflite')
    parser.add_argument('--default_job_type', help='default job type run on startup',
                        default='person_detection')
    parser.add_argument('--top_k', type=int, default=3,
                        help='number of categories with highest score to display')
    parser.add_argument('--threshold', type=float, default=0.4,
                        help='confidence score threshold')
    parser.add_argument('--input_queue', type=str, default="interpreter",
                        help='input job queue for interpreter')
    parser.add_argument('--output_queue', type=str, default="notifier",
                        help='output job queue for interpreter')
    parser.add_argument('--job_timeout', type=int, default=30,
                        help='how long until job runs out of time in seconds')
    parser.add_argument('--output_dir', type=str, default="./output",
                        help='output desitnation for interpreter completed jobs')
    args = parser.parse_args()

    logger = load_logger(logging.DEBUG)

    if os.path.isdir(args.output_dir) == False:
        os.makedirs(args.output_dir, exist_ok = True)

    try:
        connection, channel = load_rabbitmq(args)
        run(args, channel, logger)
        requeued_messages = channel.cancel()
        logger.info('Requeued %i messages' % requeued_messages)
        connection.close()
    except pika.exceptions.AMQPConnectionError as e:
        logger.error('Error connecting to RabbitMQ service: {}. Exiting...'.format(e))

if __name__ == '__main__':
    main()