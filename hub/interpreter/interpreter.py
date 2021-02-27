import cv2
import pika
import socketio
import async_timeout
import asyncio
#from PIL import Image
from io import BytesIO
import base64
import os
import json
import datetime
import time
import helper
import logging
from variables import Variables
from pycoral.adapters.detect import get_objects
from pycoral.utils.edgetpu import run_inference

sio = None
result = {}
logger = None

TOP_K = 5
THRESHOLD = 0.5

def process_webstream(timeout_seconds, interpreter, inference_size, source):
    global result,sio, logger
    result = {}
    sio = socketio.Client()
    try:
        with async_timeout(timeout_seconds):
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
                global result, sio, logger, TOP_K, THRESHOLD
                try:
                    #image = Image.open(BytesIO(base64.b64decode(message['data'])))
                    image = BytesIO(base64.b64decode(message['data']))
                    start = time.time()
                    run_inference(interpreter, image)
                    logger.debug('Interpreted image in {} ms'.format(1000*(time.time() - start)))
                    objects = get_objects(interpreter, THRESHOLD)[:TOP_K]
                    image = helper.append_objs_to_img(cv2_im, inference_size, objs, labels)
                    if len(objects) > 0:
                        logger.info('Person detected!')
                        filepath = os.path.join(args.output_dir, '{}.jpg'.format(datetime.datetime.now()))
                        result = {
                            'message': 'INTRUDER FOUND',
                            'file': filepath
                        }
                        await image.save(filepath)
                        await sio.disconnect()
                except Exception as e:
                    logger.debug('Error parsing message from socketio server: {}'.format(e))
                    result = {
                        'message': 'INTERPRETER_ERROR: {}'.format(e)
                    }
                    await sio.disconnect()
            logger.debug('Connecting to {} at {}'.format(source, time.time()))
            sio.connect(source)
    except asyncio.TimeoutError as e:
        logger.debug('Disconnecting. Job expired: {}'.format(e))
        result = {
            'message': 'OKAY: {}'.format(e)
        }
        sio.disconnect()
    except Exception as e:
        logger.error('Exception processing stream: {}'.format(e))
        result = {
            'message': 'EXCEPTION: {}'.format(e)
        }
    return result

def run(args, channel):
    global logger
    interpreter, inference_size = helper.load_interpreter(os.path.join(args.model_dir, args.model), os.path.join(args.model_dir, args.labels))
    for method_frame, _, body in channel.consume('interpreter'):
        logger.info('New RabbitMQ message: {}'.format(body))
        try:
            source = load_job(body)
            result = process_webstream(args.timeout_seconds, interpreter, inference_size, source)
            channel.basic_publish(exchange='', routing_key='notifier', body=json.dumps(result))
            channel.basic_ack(method_frame.delivery_tag)
        except pika.exceptions.ConnectionClosed as e:
            logger.error('Error notifying job complete: {}'.format(e))
            return

def main():
    global logger
    args = Variables()
    logger = helper.load_logger(logging.DEBUG)
    if os.path.isdir(args.output_dir) == False:
        os.makedirs(args.output_dir, exist_ok = True)
    connection_attempts = 0
    while True:
        try:
            connection, channel = helper.load_rabbitmq(args.rabbitmq_host, args.rabbitmq_user, args.rabbitmq_password)
            run(args, channel)
            requeued_messages = channel.cancel()
            logger.info('Requeued %i messages' % requeued_messages)
            connection.close()
        except pika.exceptions.AMQPConnectionError as e:
            logger.error('Error opening connecting to RabbitMQ service: ' + str(e))
            connection_attempts += 1
            if connection_attempts >= 5:
                logger.error('Failed connecting to RabbitMQ service after 5 attempts. Exiting...')
                break
            else:
                time.sleep(5)
                continue
        except pika.exceptions.AMQPChannelError as e:
            logger.error('Error opening channel on RabbitMQ service: ' + str(e))
            break
        except pika.exceptions.ConnectionClosedByBroker as e:
            logger.error('Error from connection closed by broker for RabbitMQ: ' + str(e))
            break

if __name__ == '__main__':
    main()