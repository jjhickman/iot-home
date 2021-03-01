import cv2
import pika
import socketio
import aiohttp
from async_timeout import timeout
import asyncio
from PIL import Image
from io import BytesIO
import base64
import os
import json
import datetime
import time
import helper
import logging
import requests
from variables import Variables
from pycoral.adapters import common
from pycoral.adapters import detect

sio = None
result = {}
logger = None
interpreter = None
TOP_K = 5
THRESHOLD = 0.5

async def process_webstream(timeout_seconds, inference_size, source, labels, output_dir):
    global result,sio, logger, interpreter
    result = {}
    sio = socketio.AsyncClient()
    try:
        async with timeout(timeout_seconds):
            @sio.event
            async def connect():
                global logger
                logger.debug('Connected at {}! Processing stream...'.format(datetime.datetime.now()))

            @sio.on('image')
            async def on_image(message):
                global result, sio, logger, TOP_K, THRESHOLD, interpreter
                try:
                    decoded = base64.b64decode(message)
                    image = Image.open(BytesIO(decoded))
                    _, scale = common.set_resized_input(interpreter, image.size, lambda size: image.resize(size, Image.ANTIALIAS))
                    interpreter.invoke()
                    objects = detect.get_objects(interpreter, THRESHOLD, scale)[:TOP_K]
                    if len(objects) > 0:
                        logger.debug('Person detected!')
                        filepath = os.path.join(output_dir, '{}.jpg'.format(datetime.datetime.now()))
                        result = {
                            'message': 'INTRUDER FOUND',
                            'file': filepath
                        }
                        image.save(filepath)
                        await sio.disconnect()
                except Exception as e:
                    logger.debug('Error parsing message from socketio server: {}'.format(e))
                    result = {
                        'message': 'INTERPRETER_ERROR: {}'.format(e)
                    }
                    await sio.disconnect()
            await sio.connect(source)
            await sio.wait()
    except asyncio.TimeoutError as e:
        await sio.disconnect()
        logger.debug('Disconnecting. Job expired')
        result = {
            'message': 'OKAY'
        }
    except Exception as e:
        logger.error('Exception processing stream: {}'.format(e))
        result = {
            'message': 'EXCEPTION: {}'.format(e)
        }
    return result

def run(args, channel):
    global logger, interpreter
    interpreter, inference_size, labels = helper.load_interpreter(os.path.join(args.model_dir, args.model), os.path.join(args.model_dir, args.labels))
    for method_frame, _, body in channel.consume('interpreter'):
        logger.info('New RabbitMQ message: {}'.format(body))
        try:
            source = helper.load_job(body)
            loop = asyncio.get_event_loop()
            result = loop.run_until_complete(asyncio.gather(process_webstream(args.timeout_seconds, inference_size, source, labels, args.output_dir)))
            channel.basic_publish(exchange='', routing_key='notifier', body=json.dumps(result))
            channel.basic_ack(method_frame.delivery_tag)
            logger.info('Published to notifier: ' + str(json.dumps(result)))
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
            channel.queue_declare('interpeter', durable=True, exclusive=False, auto_delete=False)
            channel.queue_declare('notifier', durable=True, exclusive=False, auto_delete=False)
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