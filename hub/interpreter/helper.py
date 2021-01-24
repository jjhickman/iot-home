import cv2
import pika
import os
import json
import re
import datetime
import time
import logging
import logging.handlers

from pycoral.adapters.common import input_size
from pycoral.utils.dataset import read_label_file
from pycoral.utils.edgetpu import make_interpreter

def load_rabbitmq(args):
    credentials = pika.PlainCredentials(args.rabbitmq_user, args.rabbitmq_password)
    parameters = pika.ConnectionParameters(host=args.rabbitmq_host, credentials=credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.basic_qos(prefetch_count=1) # tell RabbitMQ not to give more than one message at a time
    return connection, channel

def load_logger(log_level):
    log_formatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
    logger = logging.getLogger('interpreter')
    logger.setLevel(log_level)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    logger.addHandler(console_handler)
    return logger

def load_interpreter(model, labels):
    interpreter = make_interpreter(model)
    interpreter.allocate_tensors()
    labels = read_label_file(labels)
    inference_size = input_size(interpreter)
    return interpreter, inference_size

def load_job(args, current_job_type, interpreter, job):
    try:
        data = json.loads(job)
        source = data['source']
        job_type = data['job_type']
        if job_type != current_job_type:
            interpreter, inference_size = load_interpreter(os.path.join(args.model_dir, JOBS[job_type]['model']), os.path.join(args.model_dir, JOBS[job_type]['labels']))
        return job_type, interpreter, inference_size, source
    except ValueError as e:
        return '', None, None, ''
    except KeyError as e:
        return '', None, None, ''

def append_objs_to_img(cv2_im, inference_size, objs, labels):
    height, width, channels = cv2_im.shape
    scale_x, scale_y = width / inference_size[0], height / inference_size[1]
    for obj in objs:
        bbox = obj.bbox.scale(scale_x, scale_y)
        x0, y0 = int(bbox.xmin), int(bbox.ymin)
        x1, y1 = int(bbox.xmax), int(bbox.ymax)

        percent = int(100 * obj.score)
        label = '{}% {}'.format(percent, labels.get(obj.id, obj.id))

        cv2_im = cv2.rectangle(cv2_im, (x0, y0), (x1, y1), (0, 255, 0), 2)
        cv2_im = cv2.putText(cv2_im, label, (x0, y0+30),
                             cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 0, 0), 2)
    return cv2_im