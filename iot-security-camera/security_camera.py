from queue import Queue
import threading
import datetime 
import time
import json
import socket
import logging
import boto3
import http.client
import picamera
import detector
import streamer

def setup_log(log_directory):
    formatter = logging.Formatter('%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s] %(message)s')
    logger = logging.getLogger()
    
    file_handler = logging.FileHandler('{0}/{1}.log'.format(log_directory, 'security-camera'))
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

def run(config):
    with picamera.PiCamera(resolution='640x480', framerate=30) as camera:
        q = Queue(5)
        output = streamer.StreamingOutput(q)
        camera.start_recording(output, format='mjpeg')
        watcher = detector.Detector(config, q)
        server = streamer.StreamingServer(('', 8000), streamer.StreamingHandler)

        watch_thread = threading.Thread(target=watcher.run, daemon=True, args=())
        stream_thread = threading.Thread(target=server.serve_forever, daemon=True, args=())
        try:
            watch_thread.start()
            stream_thread.start()
            s3 = boto3.client('s3', region_name='us-east-1',aws_access_key_id=configuration['access_key_id'], aws_secret_access_key=configuration['secret_access_key'])
            device = socket.gethostname()
            while True:
                if not q.empty():
                    name = q.get()
                    connection = http.client.HTTPSConnection(config['iot_hub_hostname'])
                    headers = {'Content-type': 'application/json'}
                    notification = {'device': device, 'event': 'motion', 'stream_url': device + ':8000'}
                    connection.request('POST', '/security/camera/' + device, json.dumps(notification), headers)
                    response = connection.getresponse()
                    if response.status != 200:
                        pathname = config['log_directory'] + '/' + name
                        camera.capture(pathname, use_video_port=True)
                        s3.upload_file(Bucket = configuration['s3_bucket_name'], Filename=pathname, Key=name)
                    q.task_done()
                    time.sleep(0.2)
        finally:
            camera.stop_recording()
            stream_thread.join(5)
            watch_thread.join(5)


with open('config.json') as f:
  configuration = json.load(f)
  setup_log(configuration['log_directory'])
  run(configuration)