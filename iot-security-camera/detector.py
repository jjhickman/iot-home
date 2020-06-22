import RPi.GPIO as GPIO
import time
import requests
import datetime
import logging
import subprocess
from queue import Queue
import boto3
import socket

class Detector:
    def __init__(self, configuration, q):
        self.queue = q
        self.phone_hostname = configuration['phone_hostname']
        self.hostname = socket.gethostname()
        self.logger = logging.getLogger()
        self.sns = boto3.client('sns', region_name='us-east-1',aws_access_key_id=configuration['access_key_id'], aws_secret_access_key=configuration['secret_access_key'])
        self.sensor = int(configuration['ir_sensor_gpio'])
        self.sns_topic_arn = configuration['sns_topic_arn']
        self.iot_hub_hostname = configuration['iot_hub_hostname']
        self.iot_hub_port = int(configuration['iot_hub_port'])
        self.s3_bucket_name = configuration['s3_bucket_name']
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.sensor, GPIO.IN)
        self.logger.debug("Security Camera Detector ready...\n")
        print("Security Camera Detector ready...\n")

    def notify_hub(self):
        payload = {'hostname': self.hostname}
        print(payload)
        self.logger.debug(payload)
        r = requests.get(self.iot_hub_hostname + '/get', params=payload, timeout=10)
        print(r)
        self.logger.debug(r)
        if r.status_code == 200:
            return True
        return False
    
    def notify_owner(self):
        print('Notifying owner at topic: ' + self.sns_topic_arn)
        dt = datetime.datetime.now() 
        utc_time = dt.replace(tzinfo = datetime.timezone.utc) 
        utc_timestamp = round(utc_time.timestamp())
        name = 'security-camera-' + str(utc_timestamp) + '.jpg'
        message = 'Intruder discovered @ ' + str(utc_timestamp) + ': https://' + self.s3_bucket_name + '.s3.amazonaws.com/' + name
        self.logger.debug(message)
        response = self.sns.publish(
            TopicArn=self.sns_topic_arn,   
            Message=message,   
            Subject='INTRUDER',
        )
        self.queue.put(name)
        print(response)
        self.logger.debug(response)
        return True

    def run(self):
        try:
            while True:
                if GPIO.input(self.sensor):
                    print("Movement detected!")
                    success = (subprocess.call(['ping', '-c', '4', self.phone_hostname]) == 0)
                    if not success:
                        success = self.notify_hub()
                        if not success:
                            success = self.notify_owner()
                    while GPIO.input(self.sensor):
                        time.sleep(0.2)
        except KeyboardInterrupt:
            GPIO.cleanup()
