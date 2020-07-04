import argparse
import collections
import common
import cv2
import time
import datetime
import numpy as np
import os
from PIL import Image
import re
import tensorflow as tf
import tflite_runtime.interpreter as tflite
from tflite_runtime.interpreter import load_delegate

ALPHA = 0.5
THRESHOLD = 0.5
IMAGE_SIZE = 96

Object = collections.namedtuple('Object', ['id', 'score', 'bbox'])

class BBox(collections.namedtuple('BBox', ['xmin', 'ymin', 'xmax', 'ymax'])):
    __slots__ = ()

class HumanDetector():
    def __init__(self, configuration):
        self.log_directory = configuration['log_directory']
        self.model_directory = configuration['model_directory']
        self.model = os.path.join(self.model_directory, configuration['model'])
        self.labels_file = os.path.join(self.model_directory, configuration['labels'])
        self.top_k = int(configuration['top_k'])
        self.camera_id = int(configuration['camera_id'])
        self.score_threshold = float(configuration['score_threshold'])
        self.clip_duration_sec = int(configuration['clip_duration_sec'])
        self.expire_time = self.clip_duration_sec
        self.video_directory = configuration['video_directory']
        self.camera_stream_url = configuration['camera_stream_url']

        print('Loading {} with {} labels.'.format(self.model, self.labels_file))

        self.interpreter = common.make_interpreter(self.model)
        self.interpreter.allocate_tensors()
        self.stream = cv2.VideoCapture(self.camera_stream_url)

    def __del__(self):
        if self.stream.isOpened():
            self.stream.release()
        cv2.destroyAllWindows()


    def append_objs_to_img(self,cv2_im, objs, labels):
        height, width, channels = cv2_im.shape
        person_detected = False
        for obj in objs:
            x0, y0, x1, y1 = list(obj.bbox)
            x0, y0, x1, y1 = int(x0*width), int(y0*height), int(x1*width), int(y1*height)
            percent = int(100 * obj.score)
            label_by_id = labels.get(obj.id, obj.id)
            label = '{}% {}'.format(percent, label_by_id)
            if obj.id == 0:
                person_detected = True
            cv2_im = cv2.rectangle(cv2_im, (x0, y0), (x1, y1), (51, 64, 100), 2)
            cv2_im = cv2.putText(cv2_im, label, (x0, y0+30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (51, 64, 100), 2)
        return person_detected, cv2_im

    def load_labels(self, path):
        p = re.compile(r'\s*(\d+)(.+)')
        with open(path, 'r', encoding='utf-8') as f:
            lines = (p.match(line).groups() for line in f.readlines())
            return {int(num): text.strip() for num, text in lines}

    def get_output(self, interpreter, score_threshold, top_k, image_scale=1.0):
        boxes = common.output_tensor(interpreter, 0)
        class_ids = common.output_tensor(interpreter, 1)
        scores = common.output_tensor(interpreter, 2)
        count = int(common.output_tensor(interpreter, 3))

        def make(i):
            ymin, xmin, ymax, xmax = boxes[i]
            return Object(
                id=int(class_ids[i]),
                score=scores[i],
                bbox=BBox(xmin=np.maximum(0.0, xmin), ymin=np.maximum(0.0, ymin), xmax=np.minimum(1.0, xmax),ymax=np.minimum(1.0, ymax)))

        return [make(i) for i in range(top_k) if scores[i] >= score_threshold]

    def detect(self, duration_sec):
        if self.error:
            return False
        human_detected = False

        labels_path = os.path.join(self.model_directory, self.labels_file)
        labels = self.load_labels(labels_path)
        utc_timestamp = round(datetime.datetime.now().replace(tzinfo = datetime.timezone.utc).timestamp())
        video_name = os.path.join(self.log_directory, 'iot-hub-detect-' + str(utc_timestamp) + '.mp4')
        expire_time = utc_timestamp + duration_sec
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(video_name, fourcc, 24.0, (640,480))
        print('Monitoring`: ' + self.camera_stream_url + ' for ' + str(duration_sec) + ' seconds...')
        while utc_timestamp < expire_time or out != None:
            ret, cv2_im = self.stream.read()
            cv2_im_rgb = cv2.cvtColor(cv2_im, cv2.COLOR_BGR2RGB)
            pil_im = Image.fromarray(cv2_im_rgb)

            common.set_input(self.interpreter, pil_im)
            self.interpreter.invoke()
            objs = self.get_output(self.interpreter, score_threshold=self.score_threshold, top_k=self.top_k)
            person_detected, cv2_im = self.append_objs_to_img(cv2_im, objs, labels)
        
            if person_detected:
                if person_detected != human_detected:
                    print('HUMAN DETECTED @ ' + str(utc_timestamp))
                human_detected = True
            if out != None:
                if expire_time <= utc_timestamp:
                    print('Finished writing ' + video_name)
                    out.release()
                    out = None
                    break
                else:
                    out.write(cv2_im)
            else:
                break
            cv2.imshow(self.camera_stream_url, cv2_im)
            utc_timestamp = round(datetime.datetime.now().replace(tzinfo=datetime.timezone.utc).timestamp())
            if cv2.waitKey(1) & 0xFF == ord('q'):
                if out != None:
                    out.release()
                    out = None
                break

        self.stream.release()
        cv2.destroyAllWindows()
        return human_detected



